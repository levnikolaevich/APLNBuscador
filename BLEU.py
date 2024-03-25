import nltk
nltk.download('punkt')
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize

# Textos de ejemplo
parrafo1 = "El gato está en la alfombra."
parrafo2 = "El gato está durmiendo en la alfombra."

# Tokenizar los textos en listas de palabras
tokenized_parrafo1 = word_tokenize(parrafo1.lower())
tokenized_parrafo2 = word_tokenize(parrafo2.lower())

# Convertir los textos tokenizados en listas de listas de palabras
references = [tokenized_parrafo1]  # Lista de referencias
hypotheses = [tokenized_parrafo2]  # Lista de hipótesis

# Calcular la puntuación BLEU
bleu_score = sentence_bleu(references, hypotheses[0])  # Calcular la puntuación BLEU para la primera hipótesis

print("Puntuación BLEU:", bleu_score)
