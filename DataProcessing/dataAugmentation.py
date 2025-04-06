import pandas as pd
import re
import pickle
import random

class DA:
    def __init__(self, df, alpha_rs=0.1, alpha_sr=0.1, alpha_ri=0.1):
        self.df = df
        self.alpha_rs = alpha_rs
        self.alpha_sr = alpha_sr
        self.alpha_ri = alpha_ri
        self.wordnet = self.load_wordnet()

    
    def load_wordnet(self):
        with open('./wordnet.pickle', 'rb') as f:
            wordnet = pickle.load(f)
        return wordnet
    

    def random_swap(self):
        df = self.df.copy()
        
        for i in range(len(df)):
            comment = df.loc[i, 'comment']
            words = comment.split()

            if len(words) > 1:
                idx1 = random.randint(0, len(words)-1)

                while True:
                    idx2 = random.randint(0, len(words)-1)
                    if idx2 != idx1:
                        break

                words[idx1], words[idx2] = words[idx2], words[idx1]
                new_comment = ' '.join(words)
                df.loc[i, 'comment'] = new_comment

        return df
    

    def synonym_replacement(self):        
        df = self.df.copy()
        n = max(1, int(self.alpha_sr * len(df)))

        for i in range(len(df)):
            comment = df.loc[i, 'comment']
            words = comment.split()

            random_word_list = list(set([word for word in words]))
            random.shuffle(random_word_list)

            num_replaced = 0
            for random_word in random_word_list:
                synonyms = self.get_synonyms(random_word)
                if len(synonyms) >= 1:
                    synonym = random.choice(synonyms)
                    words = [synonym if word == random_word else word for word in words]
                    num_replaced += 1
                if num_replaced >= n:
                    break
            
            new_comment = ' '.join(words)
            df.loc[i, 'comment'] = new_comment
        return df
    

    def get_synonyms(self, word):
            synonyms = []
            try: 
                for syn in self.wordnet[word]:
                    for s in syn.split():
                        synonyms.append(s)
            except:
                pass
            return synonyms
    

    def random_insertion(self):        
        df = self.df.copy()

        for i in range(len(df)):
            comment = df.loc[i, 'comment']
            words = comment.split()
            n = max(1, int(self.alpha_ri * len(words)))

            for _ in range(n):
                self.add_word(words)

            new_comment = ' '.join(words)
            df.loc[i, 'comment'] = new_comment

        return df
    

    def add_word(self, words):
        synonyms = []
        counter = 0
        while len(synonyms) < 1:
            if len(words) >= 1:
                random_word = words[random.randint(0, len(words)-1)]
                synonyms = self.get_synonyms(random_word)
                counter += 1
            else:
                random_word = ''
            
            if counter >= 10:
                return



if __name__ == "__main__":
    df = pd.read_csv('./Data/total.txt', sep='\t')

    # preprocessing (중복 띄어쓰기 제거)
    df.comment = df.comment.apply(lambda x: re.sub(r'\s+', ' ', x) if isinstance(x, str) else x)

    # split sexual harassment
    df_sh = df[df.bias=='gender'] 
    df_non_sh = df[df.bias!='gender']

    dataAug = DA(df_sh)

    df_rs = dataAug.random_swap()
    idx_rs = df_sh[df_rs.comment != df_sh.comment].index

    df_sr = dataAug.synonym_replacement()
    idx_sr = df_sh[df_sr.comment != df_sh.comment].index

    df_ri = dataAug.random_insertion()    
    idx_ri = df_sh[df_ri.comment != df_sh.comment].index

    df_sh_total = pd.concat([df_sh, df_rs.loc[idx_rs], df_sr.loc[idx_sr], df_ri.loc[idx_ri]])
    df_total = pd.concat([df_sh_total, df_non_sh])

    df_total.to_csv('./Data/augmented_total.txt', sep='\t', index=False)


    