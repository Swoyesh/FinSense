import pandas as pd
from Modelling.preprocessing import cleanTextPipeline
import spacy

def combined_text_generator(df: pd.DataFrame) -> pd.DataFrame:

    print("started processing")
    df['processedDescription'] = df['Description'].apply(lambda x: cleanTextPipeline(x))

    return df