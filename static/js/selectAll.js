function selects(){  
    var ele=document.getElementsByClassName('check-select-all');  
    for(var i=0; i<ele.length; i++){  
        if(ele[i].type=='checkbox')  
            ele[i].checked=true;  
    }  
}  
function deSelect(){  
    var ele=document.getElementsByClassName('check-select-all');  
    for(var i=0; i<ele.length; i++){  
        if(ele[i].type=='checkbox')  
            ele[i].checked=false;
    }    
}
function checkBox(){
    if (document.getElementById('check-selector').checked) {
        selects();
    }
    if (document.getElementById('check-selector').checked == false) {
        deSelect();
    }
}