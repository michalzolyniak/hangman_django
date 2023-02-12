import pandas as pd
from hangman_django.hangman_app.models import WordsToGuess, test_word

if __name__ == '__main__':
    def polish_words():
        df_words = pd.read_fwf('/home/michalzolyniak/Desktop/coders_lab/hangman_django/polish_words.txt')
        df_words.columns = ['word']
        df_words['country'] = '1'
        df_words = df_words.head(5)
        return df_words

    def import_words_model(df):
        # convert DataFrame to a list of dictionaries
        data = df.to_dict('records')

        # create a list of model instances
        model_instances = [WordsToGuess(**row) for row in data]

        # bulk create the model instances
        WordsToGuess.objects.bulk_create(model_instances)


#polish_words_database = polish_words()
#import_words_model(polish_words_database)
print(test_word())
