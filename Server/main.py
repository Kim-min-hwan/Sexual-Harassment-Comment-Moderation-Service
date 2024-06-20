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
project_root = os.path.dirname(os.path.dirname(current_dir))

sys.path.append(current_dir)
sys.path.append(os.path.join(project_root, 'korean-hate-speech-koelectra-master'))

from dataCrowling import save_to_csv

import argparse
from trainer import Trainer
from utils import init_logger, load_tokenizer, set_seed, MODEL_CLASSES
from data_loader import load_examples

# 기본값 설정
args = argparse.Namespace(
    task="korean-hate-speech",
    model_dir="C:/Users/minhw/Desktop/4-1/소캡디/성희롱댓글/korean-hate-speech-koelectra-master/trainModel_Medium20/",
    data_dir=".",
    pred_dir="extension/Server",
    train_file="train.txt",
    dev_file="validate.txt",
    test_file="test.txt",
    prediction_file="prediction.csv",
    model_type="koelectra-base-v2",
    model_name_or_path="monologg/koelectra-base-v2-discriminator",
    seed=42,
    train_batch_size=16,
    eval_batch_size=1,
    max_seq_len=100,
    learning_rate=5e-5,
    num_train_epochs=10.0,
    weight_decay=0.0,
    gradient_accumulation_steps=1,
    adam_epsilon=1e-8,
    max_grad_norm=1.0,
    max_steps=-1,
    warmup_proportion=0.1,
    logging_steps=200,
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 댓글 데이터를 위한 Pydantic 모델
class CommentData(BaseModel):
    title: str
    comments: List[str]

@app.post("/find_comments")
async def find_comments(comment_data: CommentData):
    try:
        pattern = re.compile(r'[\u4E00-\u9FFF]')
        title =re.sub(pattern, '', comment_data.title) # 중국어 제거
        comments = comment_data.comments
        save_to_csv(title, comments)

        test_dataset = load_examples(args, tokenizer, mode="test")
        trainer.test_dataset = test_dataset
        trainer.load_model()
        genders, hates = trainer.predict()

        '''
        def softmax(logits):
            exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))  # 안정적인 계산을 위해 최대 값을 빼줌
            probabilities = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
            return probabilities
        '''

        target_indices: List[int] = [index for index, value in enumerate(genders) if value == 1]
        target_comment: List[str] = [comments[i] for i in target_indices]

        print(target_comment)
        return {"target_comment": target_comment}

    except Exception as e:
        logging.error(f"Error processing comments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def root():
    print("hell")
    return {"message": "Hello World"}

# uvicorn extension.Server.main:app --reload
# uvicorn main:app --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem --host=0.0.0.0  