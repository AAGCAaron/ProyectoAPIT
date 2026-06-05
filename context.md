project:
  title: "¿Mi PC corre el DOOM? — Aspect-Based Sentiment Analysis (ABSA) for PC Hardware Discussions Using NLP, Transformers, and YouTube Data Mining"
  team_name: "Los Papois"
  team_number: 12
  members:

    - Capistrán Ponce Manuel Emiliano

    - Gutiérrez Contreras Aldo Aarón

    - Rivera López David Zaid

    - Suárez Guzmán Dayna Yarelly

  academic_context:
    university: "Universidad Nacional Autónoma de México (UNAM)"
    faculty:    "Facultad de Ingeniería"
    course:     "Análisis y Procesamiento Inteligente de Textos"
    professor:  "Octavio Sánchez"
    semester:   "2026-2"

language:
  prompt_language: "English"
  response_language: "Spanish"

system_prompt: |
  You are an AI research assistant specialized in:
  - Natural Language Processing (NLP)
  - Aspect-Based Sentiment Analysis (ABSA)
  - Intelligent Text Analysis and Processing
  - Computational Linguistics
  - Transformer architectures
  - Deep Learning
  - YouTube data mining
  - Academic research writing in IEEE format
  - Python development for NLP systems

  You must behave as an expert in Intelligent Text Analysis and Processing,
  capable of designing advanced NLP pipelines for noisy technical communities,
  extracting semantic relationships, identifying domain-specific aspects,
  detecting contextual sentiment, sarcasm, and hardware slang
  in YouTube comment threads related to PC hardware reviews.

  All outputs, explanations, code comments, documentation,
  and academic writing MUST be generated in formal Spanish.

  The project must maintain:
  - Academic rigor
  - Reproducibility
  - Modular software architecture
  - Experimental consistency
  - IEEE-compatible documentation standards

research_focus:
  domain: "PC Hardware Community Analysis"

  primary_goal: >
    Develop a hybrid Aspect-Based Sentiment Analysis (ABSA) system
    capable of analyzing YouTube comment threads related to PC hardware
    components such as CPUs and GPUs, identifying specific technical
    aspects and their associated sentiment polarity.

  secondary_goals:
    - "Extract real-world hardware discussions from YouTube hardware review channels."
    - "Analyze noisy technical language from gaming and reviewer communities."
    - "Detect aspect-specific sentiment in hardware discussions."
    - "Identify semantic relationships between components and opinions."
    - "Evaluate transformer-based NLP architectures."
    - "Generate visual and statistical sentiment reports."
    - "Document the entire process in IEEE format."

research_questions:
  - "How accurately can transformer-based ABSA models classify sentiment in technical YouTube comment threads?"
  - "What hardware aspects generate the most positive or negative sentiment?"
  - "How does community perception differ between AMD, Intel, and NVIDIA products?"
  - "Can contextual NLP techniques improve sentiment detection in sarcastic or noisy comments?"

hypothesis:
  main_hypothesis: >
    Transformer-based hybrid ABSA systems combined with contextual
    preprocessing and domain-specific normalization can significantly
    improve sentiment classification accuracy in technical YouTube comment threads.

data_collection:
  source_platforms:
    - "YouTube"

  target_channels:
    - "Linus Tech Tips"
    - "Gamers Nexus"
    - "Hardware Unboxed"
    - "JayzTwoCents"
    - "Bitwit"
    - "Paul's Hardware"
    - "Optimum"

  search_queries:
    - "RTX 4090 review"
    - "RTX 4080 review"
    - "RTX 4070 review"
    - "Ryzen 7000 review"
    - "Intel 13th Gen review"
    - "RX 7900 XTX review"
    - "RX 7800 XT review"
    - "GPU temperature problem"
    - "thermal throttling CPU"
    - "coil whine GPU"
    - "FPS bottleneck"
    - "best budget GPU build"

  extraction_method:
    primary_api: "YouTube Data API v3 (google-api-python-client)"

    strategy: "Mixed: hardware-focused channels + keyword-based search queries"

    extraction_tasks:
      - "Extract video metadata (title, description, channel, timestamp)"
      - "Extract top-level comment threads"
      - "Extract comment likes (score) and timestamps"
      - "Filter hardware-specific discussions"

  target_hardware:
    cpus:
      - "Ryzen 5000"
      - "Ryzen 7000"
      - "Intel 12th Gen"
      - "Intel 13th Gen"

    gpus:
      - "RTX 3000"
      - "RTX 4000"
      - "RX 6000"
      - "RX 7000"

  keywords:
    - "temperature"
    - "thermal throttling"
    - "FPS"
    - "1% low"
    - "bottleneck"
    - "stuttering"
    - "latency"
    - "undervolt"
    - "coil whine"
    - "overpriced"
    - "budget build"

  output_formats:
    - "CSV"
    - "JSON"
    - "Parquet"

dataset_annotation:
  annotation_type: "Aspect-Sentiment Pair Labeling"

  sentiment_labels:
    - "Positive"
    - "Neutral"
    - "Negative"

  annotation_strategy:
    - "Manual annotation"
    - "Rule-assisted annotation"
    - "Semi-automatic labeling"

  annotation_example:
    text: >
      Gaming performance is excellent with the RX 6600,
      but temperatures are concerning.

    labels:
      - aspect: "performance"
        sentiment: "Positive"

      - aspect: "temperature"
        sentiment: "Negative"

preprocessing:
  libraries:
    - "spaCy"
    - "NLTK"
    - "pandas"
    - "re"

  tasks:
    - "Text normalization"
    - "Tokenization"
    - "Stopword removal"
    - "Lemmatization"
    - "Noise reduction"
    - "URL removal"
    - "Emoji normalization"
    - "Hardware slang normalization"
    - "Context-aware normalization"
    - "Sarcasm-aware preprocessing"

domain_slang:
  fps: "frames per second"
  bottleneck: "performance limitation"
  undervolt: "voltage optimization"
  stutter: "frame pacing issue"
  coil_whine: "electrical noise"

aspect_categories:
  thermal:
    - "temperature"
    - "temps"
    - "cooling"
    - "thermal throttling"
    - "undervolt"

  performance:
    - "FPS"
    - "1% low"
    - "stuttering"
    - "latency"
    - "bottleneck"

  value:
    - "price"
    - "overpriced"
    - "budget"
    - "cost-benefit"

  acoustics:
    - "noise"
    - "fan noise"
    - "coil whine"

advanced_nlp:
  sarcasm_detection:
    enabled: true

  irony_detection:
    enabled: true

  contextual_negation_handling:
    enabled: true

  emoji_sentiment_mapping:
    enabled: true

absa_pipeline:
  stages:
    - "Data Collection"
    - "Dataset Annotation"
    - "Text Cleaning"
    - "Aspect Extraction"
    - "Aspect Categorization"
    - "Sentiment Classification"
    - "Evaluation"
    - "Visualization"

  extraction_methods:
    - "Dependency Parsing"
    - "Transformer Embeddings"
    - "Rule-based Extraction"

model_architecture:
  approach: "Hybrid Transformer-Based ABSA"

  candidate_models:
    - "BERT"
    - "RoBERTa"
    - "DistilBERT"
    - "DeBERTa"
    - "MiniLM"

  embedding_models:
    - "Sentence-BERT"
    - "all-MiniLM-L6-v2"

  frameworks:
    - "PyTorch"
    - "Transformers"
    - "scikit-learn"

  strategies:
    - "Fine-tuning"
    - "Zero-shot classification"
    - "Multi-label classification"
    - "Contextual semantic analysis"

experiment_configuration:
  random_seed: 42

  dataset_split:
    train: 0.70
    validation: 0.15
    test: 0.15

  max_sequence_length: 256

  optimizer: "AdamW"

  learning_rates:
    - 2e-5
    - 3e-5
    - 5e-5

  batch_size:
    training: 16
    evaluation: 32

  epochs:
    min: 3
    max: 10

  early_stopping:
    enabled: true
    patience: 2

evaluation:
  metrics:
    - "Accuracy"
    - "Precision"
    - "Recall"
    - "F1-Score"

  absa_metrics:
    - "Aspect Detection Accuracy"
    - "Aspect Sentiment Accuracy"

  confusion_matrix: true

  cross_validation:
    enabled: true
    folds: 5

visualization:
  libraries:
    - "Matplotlib"
    - "Plotly"

  charts:
    - "Aspect sentiment distributions"
    - "Hardware comparison charts"
    - "Temporal sentiment evolution"
    - "Correlation graphs"
    - "Heatmaps"

comparative_analysis:
  enabled: true

  comparisons:
    - "AMD vs NVIDIA"
    - "Intel vs AMD"
    - "Budget vs High-end GPUs"

temporal_analysis:
  enabled: true

  objectives:
    - "Analyze sentiment evolution over time"
    - "Detect controversy spikes"
    - "Analyze launch-period reactions"

academic_paper:
  format: "IEEE"

  sections:
    - "Abstract"
    - "Introduction"
    - "Related Work"
    - "Methodology"
    - "Dataset Construction"
    - "Preprocessing"
    - "Model Architecture"
    - "Experiments"
    - "Evaluation"
    - "Results"
    - "Discussion"
    - "Limitations"
    - "Future Work"
    - "Conclusions"
    - "References"

  writing_requirements:
    - "Formal academic Spanish"
    - "IEEE-compatible LaTeX structure"
    - "Reproducible methodology"
    - "Technical engineering terminology"
    - "Original experimental analysis"

limitations:
  - "YouTube comments may contain sarcasm and ambiguity."
  - "Channel and viewer bias may affect sentiment distributions."
  - "Dataset imbalance may reduce generalization."
  - "Hardware trends evolve rapidly."
  - "YouTube Data API v3 daily quota (10,000 units) limits dataset size per day."

ethical_considerations:
  pii_removal:
    enabled: true

  anonymization:
    enabled: true

  youtube_terms_compliance:
    enabled: true

deployment:
  interfaces:
    - "Streamlit"
    - "Gradio"

  inference_modes:
    - "Batch analysis"
    - "Real-time inference"

software_stack:
  programming_languages:
    - "Python"

  development_tools:
    - "Jupyter Notebook"
    - "VS Code"
    - "Git"

  libraries:
    - "google-api-python-client"
    - "Transformers"
    - "PyTorch"
    - "spaCy"
    - "NLTK"
    - "pandas"
    - "NumPy"
    - "Matplotlib"
    - "Plotly"

  documentation_tools:
    - "LaTeX"
    - "Overleaf"

deliverables:
  - "YouTube extraction scripts"
  - "Annotated dataset"
  - "Preprocessing pipeline"
  - "Hybrid ABSA implementation"
  - "Evaluation metrics and reports"
  - "Visualization dashboards"
  - "IEEE-format research paper"

assistant_behavior:
  instructions:
    - "Always explain concepts in Spanish."
    - "Generate modular and documented Python code."
    - "Provide academic-level explanations."
    - "Suggest optimizations when relevant."
    - "Use engineering terminology appropriately."
    - "Focus on reproducibility and scientific rigor."
    - "Apply advanced NLP reasoning to technical hardware discussions."
