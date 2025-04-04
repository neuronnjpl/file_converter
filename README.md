# Convertisseur pdf vers csv



Installer python(si nécessaire)


Créer un environnement virtuel python 
    pour installer les packages sans polluer l'ordi (la premiere fois)
    Se positionner dans un repertoire où se ra créé l'environnement par exemple dans le projet

    Sous Linux/Mac
        python3 -m venv penvjpl
        source penvjpl/bin/activate

    Sous Windows
        python -m venv monenv
        monenv\Scripts\activate

          
    A partir de là: 
        (monenv) 

Installer les packages dans l'environnement  

    (monenv) pip install -r requirements.txt  

Exécuter        
   
       (.monenv) PS C:\Users\lapor\PycharmProjects\file_converter\bin> python run_converter.py  --input-dir ..\assets\sample_vectoriel_1 --output-dir ../tmp --output-format csv --verbose

Exemple de Résultat:

    🗂️  Résultats enregistrés dans : ../tmp\output_2025-04-04_16-22-52
    📦 2 fichier(s) PDF trouvé(s) dans ..\assets\sample_vectoriel_1
    🚫 1 fichier(s) non-PDF ignoré(s)
    
    Processing file: 111.pdf
    Found 2 table(s) in 111.pdf
    Saved table 1 to ../tmp\output_2025-04-04_16-22-52\111\table_1.csv
    Saved table 2 to ../tmp\output_2025-04-04_16-22-52\111\table_2.csv
    
    Processing file: Test vecto.pdf
    Found 1 table(s) in Test vecto.pdf
    Saved table 1 to ../tmp\output_2025-04-04_16-22-52\Test vecto\table_1.csv
    
    ✅ Extraction terminée.
    📁 Dossier de sortie : ../tmp\output_2025-04-04_16-22-52
    📄 Fichiers PDF trouvés         : 2
    🔁 Fichiers effectivement traités : 2
    ✅ Fichiers avec tableau(x)      : 2
    🚫 Fichiers non-PDF ignorés     : 1
    ℹ️ Si une erreur concernant les fichiers temporaires apparaît, elle peut être ignorée.
