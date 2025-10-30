from classifier_class import lightWeightIntentClassifier

classifier = lightWeightIntentClassifier()

classifier.loadModel(filepath='intentClassifier.pkl')

resutl = classifier.predictQuery("What is finance?")

print(resutl)
