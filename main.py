# Comment this out if you are NOT using tracing
import os
import io
import openai
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.vectorstores import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.evaluation.qa import QAEvalChain
from langchain.embeddings import OpenAIEmbeddings
import pinecone
from utils.template import prompt_template,template
import streamlit as st
import pandas as pd
import evaluate

from langchain.chat_models import ChatOpenAI

st.title('Amity Validation Platform')

with st.expander("Prompt"):
    st.write(template)

secret_key = st.text_input("Please enter your OpenAI api key",type='password')

if secret_key:

    os.environ["OPENAI_API_KEY"] =  secret_key # put your openai key

    # pinecone 

    PINECONE_API_KEY = '9ffa659d-198e-4658-b839-efe1a9c801a6'

    PINECONE_ENV = 'asia-northeast1-gcp'

    squad_metric = evaluate.load("squad")

    embeddings = OpenAIEmbeddings()

    # llm = OpenAI(temperature=0, model_name='text-davinci-003',max_tokens=500)

    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo',max_tokens=1000)

    pinecone.init(
        api_key=PINECONE_API_KEY,  # find at app.pinecone.io
        environment=PINECONE_ENV  # next to api key in console
    )
    index_name = "bank-promotion"

    db = Pinecone.from_existing_index(embedding=embeddings,index_name=index_name)
    chain = LLMChain(llm=llm,prompt=prompt_template)


    uploaded_file = st.file_uploader('Upload Excel file', type=['xlsx'])

    # Process uploaded file
    if uploaded_file is not None:
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)

            # Display DataFrame
            st.write(df)
            data = []
            for _, row in df.iterrows():
                question = row['question']
                answer = row['answer']
                data.append({'question': question, 'answer': answer})
            button_clicked = st.button('Evaluation')
            if button_clicked:
                st.write('Button clicked!')
                st.info('Performing some action...')
                for i,j in enumerate(data):
                    docs = db.similarity_search(j['question'],k=2)
                    data[i]['CONTEXT'] = docs

                prediction = chain.apply(data)
                eval_chain = QAEvalChain.from_llm(llm)
                graded_outputs = eval_chain.evaluate(data, prediction, question_key="question", prediction_key="text")
                # Add more code or actions here based on the button click
                # Display graded outputs
                graded_texts = [output["text"] for output in graded_outputs]
                df['graded_output'] = graded_texts
                df['gpt-answer'] = [i['text'] for i in prediction]
                print("Hello")
                st.write(df)

                # make prediction from for evaluation
                # Some data munging to get the examples in the right format
                results = []
                for i in range(len(df)):
                    references = [{'answers': {'answer_start': [0], 'text': [df['answer'][i]]}, 'id': '1'}]
                    gpt_gen = [{'prediction_text': df['gpt-answer'][i], 'id': '1'}]
                    results.append(squad_metric.compute(predictions=gpt_gen, references=references)['f1'])
                print("Hello 2")
                df['confident'] = results
                ##### end of chane ######
                accuracy = df['graded_output'].value_counts()
                if "CORRECT" in accuracy:
                    percentage = (accuracy["CORRECT"] / df.shape[0]) * 100
                    st.text(f"your answer is {percentage}% correct")
                else:
                    percentage = 0
                    st.text(f"your answer is {percentage}% correct")
                print("check 2")
                # st.text(f"The Accuracy of LLMs : {accuracy}")

                excel_file = io.BytesIO()
                # Create an Excel writer object
                excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

                # Write the DataFrame to the Excel writer
                df.to_excel(excel_writer, index=False, sheet_name='Sheet1')

                # Save the contents of the Excel writer
                excel_writer.save()

                st.write('Exporting the graded outputs to Excel...')
                # st.download_button(label='Download DataFrame', data=df.to_csv(), file_name='dataframe.csv', mime='text/csv')
                # Create a download button
                st.download_button(label='Download DataFrame',
                                    data=excel_file.getvalue(),
                                    file_name='Result.xlsx',
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                st.success('Export completed!')
            else:
                st.write('Button not clicked.')
        except Exception as e:
            st.error(f"Error: {e}")


