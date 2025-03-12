const ws = new WebSocket("ws://localhost:9999/handler");

ws.onopen = function () {
    ws.send(JSON.stringify({type: "Init"}));
    ws.send(JSON.stringify({type: "Connect"}));
};

ws.onmessage = function (evt) {
    var Port_connect, received_msg = evt.data;
    console.log("初始化页面");
    const imgdata = JSON.parse(received_msg);
    const frameName = imgdata.frame_name;
    console.log("frameName",frameName);
    const imgData = `data:image/jpeg;base64,${imgdata.img_data}`;
    const liElement = document.getElementById(frameName);
    if (liElement) {
        const imgElement = document.createElement('img');
        imgElement.src = imgData;
        liElement.innerHTML = '';
        imgElement.onload = function () {
            const liWidth = liElement.offsetWidth;
            const liHeight = liElement.offsetHeight;
            imgElement.style.width = liWidth + 'px';
            imgElement.style.height = liHeight + 'px';
        };
        liElement.appendChild(imgElement);
    }
};

ws.onclose = function () {
    ws.send(JSON.stringify({type: "Close"}));
    console.log("Websockets链接关闭");
};

const feedCameraBtn = document.getElementById('feedCameraBtn');
const locateCameraBtn1 = document.getElementById('locateCameraBtn1');
const locateCameraBtn2 = document.getElementById('locateCameraBtn2');
function setBackgroundColorForAllButtons(color) {
    const buttons = document.querySelectorAll('#camera_system_change button');
    buttons.forEach(button => {
        button.style.backgroundColor = color;
    });
}

function onButtonClick(button) {
    setBackgroundColorForAllButtons('#f0f0f0');
    button.style.backgroundColor = 'green';
}

feedCameraBtn.addEventListener('click', () => onButtonClick(feedCameraBtn));
locateCameraBtn1.addEventListener('click', () => onButtonClick(locateCameraBtn1));
locateCameraBtn2.addEventListener('click', () => onButtonClick(locateCameraBtn2));

document.getElementById('styleDesign').addEventListener('click', () => {
    window.styleDesign.openNewWindow('pages/style_design.html');
});

document.getElementById('log').addEventListener('click', () => {
    window.log.openNewWindow('pages/log.html');
});

document.getElementById('systemSetting').addEventListener('click', () => {
    window.systemSetting.openNewWindow('pages/systemSetting.html');
});

let Status_Detect = true;
const detectbutton = document.getElementById('startDetect');
detectbutton.addEventListener('click', () => {
    if (Status_Detect) {
        detectbutton.style.backgroundColor = 'red';
        detectbutton.innerHTML = "停止运行";
        Status_Detect = false;
        ws.send(JSON.stringify({ type: "StartDetect" }));
    }
    else {
        detectbutton.style.backgroundColor = 'green';
        detectbutton.innerHTML = "开始运行";
        Status_Detect = true;
        ws.send(JSON.stringify({ type: "StopDetect" }));
    }
});

document.getElementById('cameraSetting').addEventListener('click', () => {
    window.cameraSetting.openNewWindow('pages/cameraSetting.html');
});

function sendData(instructions, data) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: instructions }));
        ws.send(JSON.stringify(data));
    } else {
        console.error("WebSocket is not open.");
    }
}

const selectElement = document.getElementById('peifang_options');
selectElement.addEventListener('change', function () {
    const selectedValue = selectElement.options[selectElement.selectedIndex].text;
    const isConfirmed = confirm('是否选择配方: ' + selectedValue);
    if (isConfirmed) {
        //向后端发送配方名字,让后端加载对应配方
        alert('配方: ' + selectedValue + "已加载");
    }
});

//页面加载时加载配方
window.onload = function () {
    let peifang_name_list = []
        refreshPeifangList().then(res => {
            peifang_name_list = res;
            const selectElement = document.getElementById('peifang_options');
            selectElement.innerHTML = ''; // 清空现有的选项
        
            // 为 peifang_name_list 数组中的每个文件夹名称创建一个选项
            peifang_name_list.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder; // 使用文件夹名称作为 value
                option.textContent = folder; // 使用文件夹名称作为显示文本
                selectElement.appendChild(option);
            });
        });
}

document.addEventListener('DOMContentLoaded', function () {
    const button = document.getElementById('refesh_peifang');

    button.addEventListener('click', function () {
        let peifang_name_list = []
        refreshPeifangList().then(res => {
            peifang_name_list = res;
            const selectElement = document.getElementById('peifang_options');
            selectElement.innerHTML = ''; // 清空现有的选项
        
            // 为 peifang_name_list 数组中的每个文件夹名称创建一个选项
            peifang_name_list.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder; // 使用文件夹名称作为 value
                option.textContent = folder; // 使用文件夹名称作为显示文本
                selectElement.appendChild(option);
            });
           
        });

    });

});

function refreshPeifangList() {
    let peifang_name_list;
    let directoryPath = "./PeiFang/" + 'Camera1';
    window.PF.PF_load(directoryPath);
    return new Promise((resolve, reject) => {
        window.PF.PF_Write((event, peifang_name_list) => {
            resolve(peifang_name_list);
        });
    });
}

// window.webSockets_channel.receiveMessage((event, message) => {
//     sendData("Paramters",message)
// });

