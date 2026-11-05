
figpath=source/_figures

function makelatexfigures()
{
    name=$1
    cd figures/latex
    # file tree of main program
    xelatex $name.tex
    pdf2svg $name.pdf $name.svg
    mv $name.svg ../../$figpath
    mv $name.pdf ../../$figpath
    # mv out to the original path
    rm *.log *.fls *.aux __latex*.tex *.fdb_latexmk
    cd ../../
}
function makepythonfigures()
{
    name=$1
    fmt1=$2
    fmt2=$3
    cd figures/python
    python $name.py
    mv $name.$fmt1 ../../$figpath
    mv $name.$fmt2 ../../$figpath
    # mv out to the original path
    cd ../../
}
function makeDotfigures()
{
    name=$1
    cd figures/dot
    dot -Tsvg $name.dot -o $name.svg 
    dot -Tpdf $name.dot -o $name.pdf 
    mv $name.svg ../../$figpath
    mv $name.pdf ../../$figpath
    # mv out to the original path
    cd ../../
}

# # latex figures
# makelatexfigures filetree_main
# makelatexfigures casetree_main
# makelatexfigures singlepass_Lowell

# # python figures
# makepythonfigures Gaussian_hf_2d svg pdf 
# makepythonfigures Gaussian_T_2d svg pdf 
# makepythonfigures model_helloworld svg pdf 
# makepythonfigures model_nonUniformFixedValueBC svg pdf 
# makepythonfigures model_timeDependentPerm svg pdf 
# makepythonfigures model_gmsh svg pdf 
# makepythonfigures model_3Dbox jpg pdf 
# makepythonfigures model_pipe jpg pdf 
# makepythonfigures model_singlepass jpg pdf 
# makepythonfigures model_singlepass2 jpg pdf 
# makepythonfigures model_singlepass_twolimb jpg pdf 
# makepythonfigures singlepass_Lowell2014 jpg pdf 

# # graphviz figures
# makeDotfigures map_cookbooks