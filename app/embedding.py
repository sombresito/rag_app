import torch
import numpy as np
from typing import List, Dict
from transformers import AutoTokenizer, AutoModel

_tokenizer = AutoTokenizer.from_pretrained(
    "/app/local_models/intfloat/multilingual-e5-small",
    local_files_only=True
)
_model = AutoModel.from_pretrained(
    "/app/local_models/intfloat/multilingual-e5-small",
    local_files_only=True
)
_model.eval()

def generate_embeddings(chunks: List[Dict], batch_size: int = 32) -> np.ndarray:
    texts = ["passage: " + chunk["text"] for chunk in chunks]
    embeddings = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            encoded = _tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
            output = _model(**encoded)
            cls = output.last_hidden_state[:, 0, :]
            embeddings.append(cls)
    return torch.cat(embeddings, dim=0).cpu().numpy()