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
from utils.template import prompt_template
import streamlit as st
import pandas as pd

st.title('Amity Validation Platform')

secret_key = st.text_input("Please enter your OpenAI api key")

if secret_key:

    os.environ["OPENAI_API_KEY"] =  secret_key # put your openai key

    # pinecone 

    PINECONE_API_KEY = '9ffa659d-198e-4658-b839-efe1a9c801a6'

    PINECONE_ENV = 'asia-northeast1-gcp'

    embeddings = OpenAIEmbeddings()

    llm = OpenAI(temperature=0, model_name='text-davinci-003',max_tokens=500)

    pinecone.init(
        api_key=PINECONE_API_KEY,  # find at app.pinecone.io
        environment=PINECONE_ENV  # next to api key in console
    )
    index_name = "bank-live-promo"

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
                    docs = db.similarity_search(j['question'],k=1)
                    data[i]['CONTEXT'] = docs

                prediction = chain.apply(data)
                eval_chain = QAEvalChain.from_llm(llm)
                graded_outputs = eval_chain.evaluate(data, prediction, question_key="question", prediction_key="text")
                # Add more code or actions here based on the button click
                # Display graded outputs
                graded_texts = [output["text"] for output in graded_outputs]
                df['graded_output'] = graded_texts

                st.write(df)
                print("check 1")
                accuracy = df['graded_output'].value_counts(normalize=True)[' CORRECT']
                print("check 2")
                st.text(f"The Accuracy of LLMs : {accuracy}")

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

