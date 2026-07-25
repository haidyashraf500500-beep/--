# مساعد الأحوال المدنية — مشروع RAG

نظام RAG بسيط يجيب على أسئلة عن دليل مستندات وإجراءات الأحوال المدنية المصري
(بطاقة الرقم القومي، شهادات الميلاد والوفاة، قسائم الزواج والطلاق، القيد
العائلي، جواز السفر، رخصة القيادة، الشهر العقاري، التموين والفيش).

## بنية الملفات (كل ملف مرتبط بالذي قبله)

```
01_documents.py            -> المستندات الخام (من ملف PDF مقسّمة يدوياً حسب القطاع)
02_preprocessing.py        -> import من 01: تنظيف النص العربي
03_chunking.py              -> import من 02: تقسيم لنوافذ كلمات متراكبة
04_vector_representation.py -> import من 03: تمثيل كل chunk بمتجه (embedding)
05_create_chroma_store.py   -> import من 03 و 04: بناء مخزن Chroma الدائم
06_retrieve_context.py      -> import من 05 و 04: استرجاع + بناء حزمة سياق
07_prompting.py             -> import من 06: بناء الـ Prompt + استدعاء OpenRouter
streamlit_app.py            -> import من 07: واجهة Streamlit النهائية
```

بما أن أسماء الملفات تبدأ بأرقام، لا يمكن استخدام `import 01_documents` مباشرة
في بايثون؛ لذلك كل ملف لاحق يحمّل الملف السابق عبر `importlib` (دالة
`_load_module` في أعلى كل ملف).

## التشغيل محلياً

```bash
python -m venv .venv
source .venv/bin/activate          # على ويندوز: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # ثم عدّل .env وضع مفتاحك الحقيقي فيه (لا تَرفعه أبداً)

# تشغيل كل مرحلة بشكل منفصل للتأكد (اختياري، كل ملف قابل للتشغيل بمفرده):
python 01_documents.py
python 02_preprocessing.py
python 03_chunking.py
python 04_vector_representation.py
python 05_create_chroma_store.py
python 06_retrieve_context.py
python 07_prompting.py

# تشغيل الواجهة:
streamlit run streamlit_app.py
```

## مفتاح الـ API

- **لا تكتب مفتاحك الحقيقي داخل أي ملف بايثون.**
- **لا ترفع ملف `.env` الحقيقي.** الملف المرفوع هنا هو `.env.example` فقط.
- محلياً: استخدم `.env` (مضاف إلى `.gitignore`).
- عند النشر على Streamlit Cloud: استخدم Secrets بصيغة TOML (راجع الأسفل).

## إعداد Streamlit Secrets عند النشر

1. افتح تطبيقك على Streamlit Cloud.
2. اضغط **Manage app**.
3. افتح **Secrets**.
4. أضف:

```toml
OPENROUTER_API_KEY = "your_openrouter_key_here"
OPENROUTER_MODEL = "openai/gpt-4o-mini"
```

`streamlit_app.py` يقرأ هذه القيم تلقائياً من `st.secrets` ويحقنها في
`07_prompting.py` عند التشغيل، فلا حاجة لتعديل أي كود عند النشر.

## بناء/إعادة بناء مخزن المتجهات

مخزن Chroma يُبنى تلقائياً أول مرة تشغّل فيها `06_retrieve_context.py` أو
`streamlit_app.py` إن لم يكن موجوداً. لإعادة بنائه يدوياً بعد أي تعديل على
المستندات:

```bash
python 05_create_chroma_store.py
```

## التسليم النهائي

- ملف ZIP لهذا المشروع (بدون `.env` الحقيقي وبدون مجلد `chroma_store/`).
- رابط مستودع GitHub.
- رابط تطبيق Streamlit المنشور.

### Checklist سريع
- [ ] كل الملفات المطلوبة موجودة (01 إلى 07 + streamlit_app.py + requirements.txt)
- [ ] `requirements.txt` موجود ومحدث
- [ ] لا يوجد مفتاح API حقيقي في الـ ZIP أو في GitHub
- [ ] Secrets مضبوطة بصيغة TOML صحيحة على Streamlit Cloud
- [ ] تطبيق Streamlit يعمل بدون أخطاء
- [ ] الإجابة تعتمد فعلاً على السياق المسترجَع
- [ ] الإجابة تذكر مصادرها (العناوين)
