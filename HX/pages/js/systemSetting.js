var btnChooseFile = document.getElementById("btnChooseFile");
var txtFilePath = document.getElementById("txtFilePath");
var hiddenFileInput = document.getElementById("hiddenFileInput"); 

btnChooseFile.addEventListener("click", (
    function () { 
        hiddenFileInput.click() 
    }
));

hiddenFileInput.addEventListener("change", (
    function () { 
        if (this.files && this.files.length > 0) { 
            var e = this.files[0].name; 
            txtFilePath.value = e 
        } 
    }
));