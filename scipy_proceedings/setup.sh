# Setups for compiling a paper
sudo apt-get install texlive-latex-base texlive-publishers \
                     texlive-latex-extra texlive-fonts-recommended \
                     texlive-bibtex-extra
# Need a specific version to avoid compatibility issues
pip install docutils==0.12
pip install pygments
mkdir output/joseph_hellerstein
