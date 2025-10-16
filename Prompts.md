Assignment :

Build a back-end API with the following features
1. Upload a document to a GCP Data Store
2. The size of the file can vary from 10KB - 10MB
3. The formats allowed are .pdf, .docx, .pptx
4. Read the content of the files and store them as embeddings in some vector data-store. \
5. Ensure the upload and vector embedding logic is decoupled.
6. Ensure the security controls are in place.
7. End-users can do a simple RAG on this data-store.
8. Ensure the questions asked by the end user are mapped to the right document and we answer only from those docs.
9. Use any back-end language
10. Use LLM to the RAG.


The system architecture of this

Frontend :

Login by google - in the backend it will be powered by Firebase
Once logged in, user see 2 options - Upload Page and Chat Page
Upload page -
Is to upload files, it accepts only files : .pdf, .docx, .pptx  and in the limit of “10KB - 10MB” → if not, then throw error to the user
On the upload page users can list view of the files they have uploaded in the past
This can be called by API - GET /files
Chat page -
Here user can see a simple chat window, where user can type in text box and it mimics very basic chat interface
Currently dont show chat history of previous chats
The upper nav bar will have user info of the user logged in
As user will not be able to access the files and cant chat on other’s file need to mak




Backend
Endpoints :
/auth - api that calls firebase auth and validates if the user is actually a user
This will return a jwt toke, which will be used further for many things
/upload
This uploads the files to GCP
We need to make sure we save which user has uploaded this file and also will store some ID so we can locate this in GCP
/chat
User will be able to chat with ONLY the docs he has uploaded
The request goes to the SearchService
Response is doc_name, and the english response
SearchService
It makes a request to vector db pinecone and only the docs which are stored by particular user will be queried
Background Embedding Service
The upload and embedding storage task are independent of the each other
So this is achieved by pub/sub, that GCP provides
This service will get the text content from file(pdf,docx, pptx) -> then use a chunking strategy, and then create embeddings using openai’s api and save in the vector db
When the results are retrieved for the query from user, it should also fetch the doc name also(as done in citation)




What needs to discuss
How can we achieve user-level isolation of data
We have to parse the docs, and then create embeddings out of it and store it in some vector db, but we need to make sure that one user cant query on the content of another user, how to achieve this?



---

