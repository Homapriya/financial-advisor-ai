import google.generativeai as genai

genai.configure(api_key="AIzaSyDSc4qle0skmtHQ0ALHod2-A74Xlllf8os")

for model in genai.list_models():
    print(model.name)