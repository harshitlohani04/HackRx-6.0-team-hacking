# DocQuery AI
**This project was created as a part of the Bajaj HackRx-6.0 hackathon.**

This project is a **FastAPI-based API** service that processes and retrieves information from documents using **LangChain** and **Groq LLM** for intelligent query handling. Users can upload pdf blob url various sources, which are then processed through an ingestion pipeline involving chunking, embedding generation, and storage for semantic search. The system is deployed on Modal for scalable and serverless execution, with environment-based configuration for secure API key management.


## Testing the API

Testing of the api can be done using Postman(https://www.postman.com/). Install the application or use the website for creating the POST request to the following api endpoint.

**Deployment link** : https://kartiklohani2004--hackrx-team-hacking-fastapi-app.modal.run

#### POST Request

```http
  POST /hackrx/run
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `documents` | `string` | **Required**. The blob url for the document. |
| `questions` | `list[string]` | **Required**. A list of questions that are to be asked regarding the document. |

The request also required an Authorization Bearer token in the header that serves the purpose of verifying the user for accessing the service.

Overall the input looks like :

``` json
POST /hackrx/run
Content-Type: application/json
Accept: application/json
Authorization: Bearer <api-token>

{
  "document": "https://hackrx.blob.core.windows.net/assets/hackrx_6/policies/EDLHLGA23009V012223.pdf?sv=2023-01-03&st=2025-07-30T06%3A46%3A49Z&se=2025-09-01T06%3A46%3A00Z&sr=c&sp=rl&sig=9szykRKdGYj0BVm1skP%2BX8N9%2FRENEn2k7MQPUp33jyQ%3D",
  "questions": ["does the policy cover suicides?", "What is the maximum travel distance covered under this benefit?", "In what type of medical situation is an air ambulance covered?"]
}
```

### Response

The API endpoint gives a json format output for the request, the output looks like : 
```json
{
    "answers": [
        "No, the policy does not cover suicide.",
        "The maximum travel distance covered under this benefit is 150 kms.",
        "According to the provided text, an air ambulance is covered when the Insured Person requires Emergency Care for an Accident/Illness, and Medically Necessary Treatment cannot be provided at the Hospital where the Insured Person is situated at the time of requiring Emergency Care."
    ]
}
```

## Deployment

**Modal** was used for deployment in this project.
To deploy this project run

```bash
  modal token new # this is to create a new modal token for the deployment.
  modal deploy modal_app.py
```
