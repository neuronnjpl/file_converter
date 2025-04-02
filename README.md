Convertisseur



Installer python(si necessaire)
    sudo apt install python3 python3-pip
    python3 --version
    pip3 --version

Creer un environnement python pour installer les packages sans poluer l'ordi (la premiere fois)
    Se positionner dans un repertoire où se ra créé l'environnement par exemple dans le projet

    Sous Linux/Mac
        python3 -m venv penvjpl
        source penvjpl/bin/activate


Installer les packages dans l'environnement  
    pip install -r requirements.txt  

Executer        
    python3 camelot_converter.py ../tableau_exemple_helvetica.pdf --output-dir ../tmp --output-format csv --verbose
