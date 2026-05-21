import traceback
import sys

from rag import RAGManager
rag = RAGManager()
print("rag loaded")

texto_usuario = "hola"
try:
    print("buscar_contexto")
    contexto = rag.buscar_contexto(texto_usuario)
    print("buscar_memoria_reciente")
    memoria = rag.buscar_memoria_reciente(texto_usuario)
    print("Done")
except Exception as e:
    traceback.print_exc()

