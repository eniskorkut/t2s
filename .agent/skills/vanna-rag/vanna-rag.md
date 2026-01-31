---
name: vanna-rag
description: Expert guidelines for Vanna AI (Text-to-SQL) framework integration, training strategies, and RAG pipeline management.
---

# Vanna AI & RAG Mastery

This skill defines the **Standard Operating Procedures (SOP)** for interacting with the Vanna AI framework in the `t2s` project.

## 1. 🧠 Training Strategy (How to Teach Vanna)

Vanna learns in three specific ways. Use them in this priority order to minimize hallucinations:

### A. DDL (Schema) Training - *The Foundation*
The model MUST know the database structure perfectly.
- **Source of Truth:** Always refer to `vanna-main-backend/DATABASE_SCHEMA.txt`.
- **Code Pattern:**
  ```python
  vn.train(ddl="CREATE TABLE users (id INT, name TEXT, signup_date DATE...)")