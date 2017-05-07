# Setups for compiling a paper
mkdir output/joseph_hellerstein
sudo apt-get install texlive-latex-base texlive-publishers \
                     texlive-latex-extra texlive-fonts-recommended \
                     texlive-bibtex-extra
# Need a specific version to avoid compatibility issues
pip install docutil==0.12
pip install pygments
