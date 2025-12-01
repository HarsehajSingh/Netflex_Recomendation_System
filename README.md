# 🎬 Netflex Recommendation System

An AI-powered movie recommendation web app built as an **ADS Project**, using Python and similarity-based matching.  
Users can search for a movie and instantly get a list of similar movies along with detailed information.

> **Author:** Harsehaj Singh  
> **Roll No:** 2410998532  
> **Project:** ADS – Netflex Recommendation System  

---

## 🚀 Features

- 🔍 Fuzzy search for movie titles (even with slight spelling mistakes)  
- 🎯 Content-based recommendations using a precomputed similarity matrix  
- 📄 Displays detailed movie information  
- ⚡ Fast recommendations using `.pkl` data files  
- 🖥️ Simple and interactive UI built with Streamlit  

---

## 🧱 Tech Stack

- **Language:** Python  
- **Framework:** Streamlit  
- **Libraries:** Pandas, Pickle, PIL  
- **Model Type:** Similarity-based recommendation system  
- **Data Files:** `movies.pkl`, `similarity.pkl`  

---

## 📌 Import Modules Used

The following Python modules are used in the project:

```python
import streamlit as st
import pandas as pd
import pickle
from difflib import get_close_matches
from typing import List
import io
from PIL import Image, ImageDraw, ImageFont

Drive link for both datasets
https://drive.google.com/drive/folders/1jdJwJ7HkRw-JwIxNZpAQHvc_2_2syCpa
https://drive.google.com/drive/folders/1jdJwJ7HkRw-JwIxNZpAQHvc_2_2syCpa?usp=drive_link
