import os
import sys
import logging
import re
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

sys.path.append(os.path.join(project_root, "Model"))
sys.path.append(os.path.join(project_root, "DataProcessing"))

import argparse
from dataCrowling import save_to_csv
from trainer import Trainer
from utils import init_logger, load_tokenizer, set_seed, MODEL_CLASSES
from data_loader import load_examples

# argument 기본값 설정
args = argparse.Namespace(
    task="korean-sexual-harrassment-detection",
    model_dir="./trainModel/",
    data_dir='.',
    pred_dir="Prediction",
    train_file="train.txt",
    dev_file="validate.txt",
    test_file="test.txt",
    prediction_file="prediction.csv",
    model_type="koelectra-base-v2",
    model_name_or_path="monologg/koelectra-base-v2-discriminator",
    seed=42,
    train_batch_size=16,
    eval_batch_size=1,
    max_seq_len=20,
    learning_rate=5e-5,
    num_train_epochs=10.0,
    weight_decay=0.0,
    gradient_accumulation_steps=1,
    adam_epsilon=1e-8,
    max_grad_norm=1.0,
    max_steps=-1,
    warmup_proportion=0.1,
    do_train=False,
    do_pred=True,
    no_cuda=False,
    bias_loss_coef=0.5,
    hate_loss_coef=1.0
)
init_logger()
set_seed(args)
tokenizer = load_tokenizer(args)
trainer = Trainer(args, tokenizer)


app = FastAPI()
# 다른 도메인의 요청을 받아들일 수 있도록 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 댓글 데이터를 위한 Pydantic 모델
# Pydantic: 데이터 유효성 검사 및 직렬화 역할, FastAPI에서 요청, 응답하는 json 파일을 python 객체로 변환
class CommentData(BaseModel):
    title: str
    comments: List[str]

@app.post("/find_comments")
async def find_comments(comment_data: CommentData):
    pattern = re.compile(r'[\u4E00-\u9FFF]')
    title =re.sub(pattern, '', comment_data.title) # 한자 제거
    comments = comment_data.comments
    save_to_csv(title, comments)

    test_dataset = load_examples(args, tokenizer, mode="test")
    trainer.test_dataset = test_dataset
    trainer.load_model()
    genders, hates = trainer.predict()

    target_indices: List[int] = [index for index, value in enumerate(genders) if value == 1]
    target_comment: List[str] = [comments[i] for i in target_indices]

    return {"target_comments": target_comment}

    
@app.get("/")
async def root():
    return {"message": "Hello World"}

''' 실행 방법
1. default -> uvicorn Server.main:app --reload
2. https에 의해 ssl keyfile 적용 시 -> uvicorn main:app --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem --host=0.0.0.0
'''