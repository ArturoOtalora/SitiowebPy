from transformers import pipeline
from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pyodbc
import random

conexion = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=DESKTOP-B1LS0KA\\SQLEXPRESS;"
    "DATABASE=Neurona;"
    "Trusted_Connection=yes;"
)

app = FastAPI()
qa_pipeline = pipeline("question-answering", model="distilbert-base-multilingual-cased")

preguntas_sets = [
    ["¿Piensas que tu alimentación te nutre?", "¿Practicas ejercicios?", "¿Duermes bien?", "¿Tus hábitos ayudan a cuidar tu cuerpo?"],
    ["Cuando fracasas en una tarea, ¿lo superas con facilidad?", "¿Cuando sabes que estás siendo evaluado por los demás, ¿consigues mantenerte tranquila/o?", "¿Si alguien critica el trabajo que haces, ¿Cómo te sientes?", "¿Crees tener buena autoestima?"],
    ["Cuando no alcanzas un objetivo para el que te creías capaz, ¿Qué haces?", "¿¿Te gusta el desafío de hacer tareas nuevas? (Aunque no sepas si tienes las habilidades necesarias para tener éxito)?", "¿Cuando fracasas en una tarea, ¿eres capaz de reírte de ti mismo?", "¿Cuando fracasas en una tarea, ¿sientes que la gente que te quiere te seguirá apoyando?"],
    ["¿Acostumbras lamentarte con amigos y familiares de las cualidades o habilidades que no tienes?", "¿Piensas con frecuencia en las veces que no lograste lo que querías?", "¿Eres una persona competitiva?", "¿Si la persona que te gusta te deja plantada/o, ¿Qué haces?"],
    ["¿Te preparaste para un reto  importante y crees que no te fue bien. ¿Cómo te sientes?", "¿Tienes poco interés o placer en hacer las cosas?", "¿Te sientes desanimado/a, triste, o sin esperanza?", "¿Sientes que tienes control sobre tu vida?"]
]

class Pregunta(BaseModel):
    pregunta: str
    calificacion: int

@app.post("/guardar_respuesta")
def guardar_respuesta(pregunta: str = Form(...), calificacion: int = Form(...)):
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO respuestas (pregunta, calificacion) VALUES (?, ?)", (pregunta, calificacion))
    conexion.commit()
    return {"message": "Respuesta guardada", "pregunta": pregunta, "calificacion": calificacion}

@app.get("/", response_class=HTMLResponse)
def mostrar_pagina():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Turing</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center; padding: 50px; }
            .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); display: inline-block; text-align: left; }
            img { width: 200px; height: auto; }
            .star-rating { direction: rtl; display: inline-flex; }
            .star-rating input { display: none; }
            .star-rating label { font-size: 25px; color: #ddd; cursor: pointer; }
            .star-rating input:checked ~ label { color: gold; }
        </style>
        <script>
            let preguntasSets = """ + str(preguntas_sets) + """;
            let currentSet = 0;
            function enviarRespuestas() {
                let respuestas = document.querySelectorAll("input[type=radio]:checked");
                respuestas.forEach((respuesta, index) => {
                    fetch("/guardar_respuesta", {
                        method: "POST",
                        body: new URLSearchParams({ pregunta: preguntasSets[currentSet][index], calificacion: respuesta.value }),
                        headers: { "Content-Type": "application/x-www-form-urlencoded" }
                    });
                });
                if (currentSet < preguntasSets.length - 1) {
                    currentSet++;
                    generarPreguntas(preguntasSets[currentSet]);
                } else {
                    alert("Gracias por completar las preguntas.");
                }
            }
            function generarPreguntas(preguntas) {
                document.getElementById('preguntas-lista').innerHTML = preguntas.map((pregunta, index) => `
                    <li>
                        <p>${pregunta}</p>
                        <div class="star-rating">
                          
                            <input type="radio" name="rating-${index}" value="10" id="10-${index}"><label for="10-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="9" id="9-${index}"><label for="9-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="8" id="8-${index}"><label for="8-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="7" id="7-${index}"><label for="7-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="6" id="6-${index}"><label for="6-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="5" id="5-${index}"><label for="5-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="4" id="4-${index}"><label for="4-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="3" id="3-${index}"><label for="3-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="2" id="2-${index}"><label for="2-${index}">&#9733;</label>
                            <input type="radio" name="rating-${index}" value="1" id="1-${index}"><label for="1-${index}">&#9733;</label>
                        </div>
                    </li>`).join('');
            }
            window.onload = function() {
                generarPreguntas(preguntasSets[currentSet]);
            }
        </script>
    </head>
    <body>
        <img src="https://centromedicoabc.com/core/webp-express/webp-images/uploads/2023/01/salud-mental-1024x634.jpg.webp" alt="Logo">
        <h1>Bienvenidos a un lugar seguro donde tus pensamientos y emociones pueden ser escuchados y comprendidos</h1>
        <div class="container">
            <h2>Responde las siguientes preguntas:</h2>
            <ul id="preguntas-lista"></ul>
            <button onclick="enviarRespuestas()">Siguiente</button>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
