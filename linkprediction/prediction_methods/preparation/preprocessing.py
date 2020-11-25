from collections import Counter


def preprocess_df(df):
    processed_df = df.copy()
    zero = Counter(processed_df.label.values)[0]
    un = Counter(processed_df.label.values)[1]
    n = zero - un
    processed_df['label'] = processed_df['label'].astype('category')
    processed_df = processed_df.drop(
        processed_df[processed_df.label == 0].sample(n=n, random_state=1).index)
    return processed_df.sample(frac=1)