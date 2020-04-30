import re
import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import ward, dendrogram, fcluster
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt



def tokenizer(text):
	is_stemmed = True

	# first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
	tokens = []
	for sent in nltk.sent_tokenize(text):
		for word in nltk.word_tokenize(sent):
			tokens.append(word)
	tokens_filtered = []

	# filter out any tokens not containing letters 
	# (e.g., numeric tokens, raw punctuation)
	for token in tokens:
		if re.search('[a-zA-Z]', token):
			if is_stemmed:
				stemmer = SnowballStemmer("english")
				tokens_filtered.append(stemmer.stem(token))
			else:
				tokens_filtered.append(token)
	return tokens_filtered



def generate_linkage_matrix(content, max_features, min_df, max_df, use_idf, min_ngram, max_ngram):
	tfidf_vectorizer = TfidfVectorizer(
		max_features=max_features,
		min_df=min_df,
		max_df=max_df,
		use_idf=use_idf,
		ngram_range=(min_ngram, max_ngram),
		tokenizer=tokenizer,
		stop_words='english',
	)
	tfidf_matrix = tfidf_vectorizer.fit_transform(content)
	dist = 1 - cosine_similarity(tfidf_matrix)
	linkage_matrix = ward(dist)
	return linkage_matrix



def auto_select_num_clusters(linkage_matrix):
	acceleration = np.diff(linkage_matrix, 2)
	acceleration_rev = acceleration[::-1]
	num_clusters = acceleration_rev.argmax() + 2
	return num_clusters



def generate_clustering(linkage_matrix, num_clusters):
	return fcluster(linkage_matrix, num_clusters, criterion='maxclust').tolist()



def plot_dendrogram(linkage_matrix, num_clusters, idx, dendrogram_path):

	# set size
	fig, ax = plt.subplots(figsize=(15, 20))
	ax = dendrogram(linkage_matrix, orientation="right", labels=idx);

	# select distance cut-off
	max_d = (linkage_matrix[-num_clusters][2] + linkage_matrix[-num_clusters + 1][2]) / 2

	# plot the cut-off line at x=max_d
	plt.axvline(x=max_d, c='k')

	# changes apply to the x-axis
	# both major and minor ticks are affected
	# ticks along the bottom edge are off
	# ticks along the top edge are off
	plt.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='off')

	# show plot with tight layout
	plt.tight_layout()

	# save figure as ward_clusters
	plt.savefig(dendrogram_path, dpi=200)

	plt.close()