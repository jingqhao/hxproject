const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld(
    'styleDesign', {
    openNewWindow: (filePath) => {
        ipcRenderer.send('style-design', filePath);
    }
}
);

contextBridge.exposeInMainWorld(
    'log', {
    openNewWindow: (filePath) => {
        ipcRenderer.send('log', filePath);
    }
}
);

contextBridge.exposeInMainWorld(
    'systemSetting', {
    openNewWindow: (filePath) => {
        ipcRenderer.send('systemsetting', filePath);
    }
}
);

contextBridge.exposeInMainWorld(
    'paramter', {
    openNewWindow: (filePath, cameraID, peifang_name, type) => {
        ipcRenderer.send('paramter', filePath, cameraID, peifang_name, type);
    }
}
);

contextBridge.exposeInMainWorld(
    'cameraSetting', {
    openNewWindow: (filePath) => {
        ipcRenderer.send('camerasetting', filePath);
    }
}
);

// 接收和发送
contextBridge.exposeInMainWorld('webSockets_channel', {
    sendMessage: (message) => {
        ipcRenderer.send('s_message', message)
    },
    receiveMessage: (message) => {
        ipcRenderer.on('r_message', message)
    }
});

contextBridge.exposeInMainWorld('ParamSave', {
    sendParam: (Paramter,base64Image) => {
        ipcRenderer.send('s_param', Paramter,base64Image)
    },
});

contextBridge.exposeInMainWorld('PF', {
    PF_load: (directoryPath) => ipcRenderer.send('read_PF', directoryPath),
    PF_Write: (peifangNameList) => ipcRenderer.on('write_PF', peifangNameList)
});

contextBridge.exposeInMainWorld('Product_type_ParamSave', {
    sendParam: (Paramter,path) => {
        ipcRenderer.send('send_product_type_param', Paramter,path)
    },
});

contextBridge.exposeInMainWorld('rename', {
    sendParam: (cameranum,oldname,newname) => {
        ipcRenderer.send('send_names', cameranum,oldname,newname)
    },
});

