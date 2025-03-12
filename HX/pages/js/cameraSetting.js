const ws = new WebSocket("ws://localhost:9999/handler");

ws.onopen = function () {
    ws.send(JSON.stringify({type: "Init"}));
    ws.send(JSON.stringify({type: "CamSettingInit"}));
    ws.send(JSON.stringify({type: "CamSetting"}));
};

//下拉框展示
const dropdownMenu = document.getElementById("dropdownMenu");
// 获取输入框和滚动条元素
const exposureInput = document.getElementById('exposure');
const brightnessInput = document.getElementById('brightness');
const contrastInput = document.getElementById('contrast');
const getRotateREBtn = document.getElementById('RotateREBtn');
const choiceCameras = document.getElementById('choiceCameras');
const getFlipREBtn = document.getElementById('FlipREBtn');
const saveDataBtn = document.getElementById('saveDataBtn');
let angleNum = -1;
let flipParam = -1;
let verticalFlip = false;
let horizontalFlip = false;

ws.onmessage = function (evt) {
    var Port_connect, received_msg = evt.data;
    const dataObj = JSON.parse(received_msg);
    const type = dataObj.type;
    const data = dataObj.data;
    const params = dataObj.params
    if (type == "CamSettingInit"){
        //获取相机数量
        console.log("params",params)
        angleNum = parseInt(params[0]);
        const exposure = parseInt(params[1]);
        const brightness = parseInt(params[2]);
        const contrast = parseInt(params[3]);
        const camerasNum = parseInt(data);
        updateDropdownMenu(camerasNum);
        updateCamerasParams(exposure, brightness, contrast);
    }else if(type == "CamSetting" || "RotateImage"){
        console.log("data", data);
        const encoded_frames = data[0];
        const frameName = encoded_frames.frame_name;
        const imgData = `data:image/jpeg;base64,${encoded_frames.img_data}`;   
        const liElement = document.getElementById("artifact_view");
        if (liElement) {
            const imgElement = document.createElement('img');
            const liWidth = liElement.offsetWidth;
            const liHeight = liElement.offsetHeight;
            imgElement.style.width = liWidth + 'px';
            imgElement.style.height = liHeight + 'px';
            // 矩形图像框
            // if(angleNum == -1 || angleNum == 1){
            //     imgElement.style.width = liWidth + 'px';
            //     imgElement.style.height = liHeight-40 + 'px';
            // }else if(angleNum == 0 || angleNum == 2){
            //     imgElement.style.width = liWidth-40 + 'px';
            //     imgElement.style.height = liHeight + 'px';
            // }
            imgElement.src = imgData;
            liElement.innerHTML = '';
            // imgElement.onload = function () {
                
            // };
            liElement.appendChild(imgElement);
        }
    }
    // console.log("liElement",liElement)
};

ws.onclose = function () {
    ws.send(JSON.stringify({type: "Close"}));
    console.log("Websockets链接关闭");
};

// 定义函数，用于处理每个选项的点击
function onDropdownMenuButtonClick(event) {
    // 获取点击的文本内容
    const selectedText = event.target.textContent;
    console.log("Selected text:", selectedText);
    
    // 将按钮文本更新为选中的内容
    if (selectedText.includes("°")) {
        console.log("°");
        getRotateREBtn.textContent = selectedText;
        console.log("angleNum-----------",  angleNum)
        if (selectedText === '0°') {
            angleNum = -1;
        } else if (selectedText === '90°') {
            angleNum = 0;
        } else if (selectedText === '180°') {
            angleNum = 1;
        } else if (selectedText === '270°') {
            angleNum = 2;
        } else if (selectedText === '0°+水平镜像') {
            angleNum = 3;
        } else if (selectedText === '0°+垂直镜像') {
            angleNum = 4;
        } else if (selectedText === '旋转90°+水平镜像') {
            angleNum = 5;
        } else if (selectedText === '旋转90°+垂直镜像') {
            angleNum = 6;
        } 
         // 向 WebSocket 发送消息
        ws.send(JSON.stringify({type: "RotateImage", angle: angleNum}));
    }else if (selectedText.includes("相机")){
        choiceCameras.textContent = selectedText;
        if (selectedText === '相机一') {
            console.log("相机一");
        } else if (selectedText === '相机二') {
            console.log("相机二");
        } else if (selectedText === '相机三') {
            console.log("相机三");
        } else if (selectedText === '相机四') {
            console.log("相机四");
        } else if (selectedText === '相机五') {
            console.log("相机五");
        } else if (selectedText === '相机六') {
            console.log("相机六");
        }
        // ws.send(JSON.stringify({type: "RotateImage", angle: angleNum}));
    }
    // 前端镜像实现：
    // else if (selectedText.includes("翻转")) {
    //     console.log("翻转");
    //     getFlipREBtn.textContent = selectedText;
    //     const image = document.getElementById("artifact_view");
    //     if (selectedText === '未翻转') {
    //         // image.style.transform = `scale(1, 1)`;
    //     } else if (selectedText === '水平翻转') {
    //         // image.style.transform = `scale(-1, 1)`;
    //     } else if (selectedText === '垂直翻转') {
    //         // image.style.transform = `scale(1, -1)`;
    //     } else if (selectedText === '水平+垂直翻转') {
    //         // image.style.transform = `scale(-1, -1)`;
    //     } 
    //     //  // 向 WebSocket 发送消息
    //     // ws.send(JSON.stringify({type: "FlipImage", flipParam: flipParam}));
    // }
}

// 生成下拉菜单选项的函数
function updateDropdownMenu(num) {
    const dropdownMenu = document.getElementById("dropdownMenu");

    // 清空现有菜单项
    dropdownMenu.innerHTML = "";

    // 根据 num 生成选项
    const options = ["相机一", "相机二", "相机三", "相机四", "相机五", "相机六"];
    for (let i = 0; i < num && i < options.length; i++) {
        const item = document.createElement("a");
        item.className = "dropdown-item";
        item.href = "#";
        item.textContent = options[i];
        dropdownMenu.appendChild(item);
    }
}

// 为每个下拉选项添加点击事件监听器
document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', onDropdownMenuButtonClick);
});

window.webSockets_channel.receiveMessage((event, message) => {
    console.log("message---");
    sendData("Paramters",message);
})

function saveParameters(){
    console.log("angleNum-----------",  angleNum)
    ws.send(JSON.stringify({type: "saveParameters", angle: angleNum}));
}

saveDataBtn.addEventListener('click', saveParameters)

//----------------------------------------------------------相机属性参数调节--------------------------------------------------------

// // 监听滚动条的 input 事件
// rangeInput.addEventListener('input', function () {
//     // 将滚动条的值同步到输入框
//     exposureInput.value = rangeInput.value;
//     ws.send(JSON.stringify({type: "ExposureTime", params: exposureInput.value}));
// });

// 获取所有具有 class="form-range" 的元素
const rangeInputs = document.querySelectorAll('.form-range');

// 遍历每个元素，添加事件监听器或进行相应的处理
rangeInputs.forEach((rangeInput, index) => {
    // 为每个输入元素添加一个事件监听器
    rangeInput.addEventListener('input', (event) => {   
        console.log(`第 ${index + 1} 个滚动条的值: ${event.target.value}`);
        if (index === 0) {console.log("index", index);exposureInput.value = event.target.value; ws.send(JSON.stringify({type: "ExposureTime", params: exposureInput.value}));}
        else if(index === 1) {console.log("index", index);brightnessInput.value = event.target.value; ws.send(JSON.stringify({type: "Brightness", params: brightnessInput.value}));}
        else if(index === 2) {console.log("index", index);contrastInput.value = event.target.value; ws.send(JSON.stringify({type: "Contrast", params: contrastInput.value}));}
    });
});

// 如果需要输入框同步滚动条值，也可以添加事件
exposureInput.addEventListener('input', function () {
    // 确保输入框的值是数字，并同步到滚动条
    const value = parseInt(exposureInput.value, 10);
    if (!isNaN(value)) {
        // 限制值在滚动条范围内
        rangeInput.value = Math.max(rangeInput.min, Math.min(rangeInput.max, value));
    }
});

// 展示相机的初始参数
function updateCamerasParams(param1, param2, param3) {
    // 获取所有具有 class="camera_params" 的元素
    const inputParams = document.querySelectorAll('.camera_params');
    inputParams.forEach((inputParam, index) => {
    // 为每个输入元素添加一个事件监
        console.log(`第 ${index + 1} 个输入框`);
        if (index === 0) {console.log("param1", param1);exposureInput.value = param1}
        else if(index === 1) {console.log("param2", param2);brightnessInput.value = param2}
        else if(index === 2) {console.log("param3", param3);contrastInput.value = param3}
    });

}