import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google import genai
import chromadb


MAX_MEMORIAS = 200


class RAGManager:

    def __init__(self):

        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        base_dir = os.path.dirname(__file__)

        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(base_dir, "chroma_db")
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="vtuber_knowledge"
        )

        self.memory_collection = self.chroma_client.get_or_create_collection(
            name="vtuber_memory"
        )

    def generar_embedding(self, texto):

        response = self.client.models.embed_content(
            model="gemini-embedding-2",
            contents=texto
        )

        return response.embeddings[0].values

    def indexar_documento(self, ruta_txt):

        if self.collection.count() > 0:
            print("ℹ️ Base ya indexada.")
            return

        if not os.path.exists(ruta_txt):

            print(f"⚠️ No existe: {ruta_txt}")

            return

        with open(ruta_txt, "r", encoding="utf-8") as f:

            lineas = [
                l.strip()
                for l in f.readlines()
                if l.strip()
            ]

        for i, linea in enumerate(lineas):

            embedding = self.generar_embedding(linea)

            self.collection.add(
                ids=[f"id_{i}"],
                embeddings=[embedding],
                documents=[linea]
            )

        print("✅ Base indexada.")

    def buscar_contexto(self, consulta):

        if self.collection.count() == 0:
            return ""

        embedding = self.generar_embedding(consulta)

        resultados = self.collection.query(
            query_embeddings=[embedding],
            n_results=2
        )

        return " ".join(resultados["documents"][0])

    def buscar_memoria_reciente(self, consulta):

        if self.memory_collection.count() == 0:
            return ""

        embedding = self.generar_embedding(consulta)

        resultados = self.memory_collection.query(
            query_embeddings=[embedding],
            n_results=2
        )

        return " ".join(resultados["documents"][0])

    def guardar_en_memoria(
        self,
        texto_usuario,
        respuesta_ia
    ):

        if self.memory_collection.count() >= MAX_MEMORIAS:

            self.memory_collection.delete(
                ids=["mem_id_0"]
            )

        documento = f"""
Usuario: {texto_usuario}

VTuber: {respuesta_ia}
"""

        embedding = self.generar_embedding(documento)

        doc_id = f"mem_id_{self.memory_collection.count()}"

        self.memory_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[documento]
        )