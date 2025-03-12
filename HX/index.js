const { app, BrowserWindow, ipcMain } = require('electron');
const Main = require('electron/main');
const path = require('path');
const fs = require('fs');
const sharp = require('sharp');



var mainWin, Param, Style;

function createWindow() {
    const win = new BrowserWindow({
        width: 1300,
        height: 880,
        autoHideMenuBar: true,
        x: 0,
        y: 0,
        webPreferences: {
            preload: path.resolve(__dirname, 'preload.js'),
            contextIsolation: true, // 必须设置为true
            nodeIntegration: false, // 禁用nodeIntegration
        }
    })  
    win.loadFile('./pages/index.html')
    mainWin = win
}

ipcMain.on('style-design', (event, filePath) => {
    const fullPath = path.join(__dirname, filePath);
    const styleDesign = new BrowserWindow({
        width: 1300,
        height: 800,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.resolve(__dirname, 'preload.js'),
            contextIsolation: true, // 必须设置为true
            nodeIntegration: false, // 禁用nodeIntegration
        }
    });
    styleDesign.loadFile(fullPath); // 加载新页面
    Style = styleDesign;
});

ipcMain.on('log', (event, filePath) => {
    const fullPath = path.join(__dirname, filePath);
    const log = new BrowserWindow({
        width: 900,
        height: 600,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.resolve(__dirname, 'preload.js'),
            contextIsolation: true, // 必须设置为true
            nodeIntegration: false, // 禁用nodeIntegration
        }
    });
    log.loadFile(fullPath); // 加载新页面
});

ipcMain.on('systemsetting', (event, filePath) => {
    const fullPath = path.join(__dirname, filePath);
    const system = new BrowserWindow({
        width: 1100,
        height: 780,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.resolve(__dirname, 'preload.js'),
            contextIsolation: true, // 必须设置为true
            nodeIntegration: false, // 禁用nodeIntegration
        }
    });
    system.loadFile(fullPath); // 加载新页面
});

ipcMain.on('paramter', (event, filePath, cameraID, peifang_name, type) => {
    const fullPath = path.join(__dirname, filePath);
    const paramter = new BrowserWindow({
        width: 1150,
        height: 850,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.resolve(__dirname, 'preload.js'),
            contextIsolation: true, // 必须设置为true
            nodeIntegration: false, // 禁用nodeIntegration
        }
    });
    paramter.loadFile(fullPath, { search: "cameraID=" + cameraID + "&" + "peifang_name=" + peifang_name + "&" + "type=" + type }); // 加载新页面
    Param = paramter;
});

ipcMain.on('camerasetting', (event, filePath) => {
    const fullPath = path.join(__dirname, filePath);
    const cameraSetting = new BrowserWindow({
        width: 1150,
        height: 850,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.resolve(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        }
    });
    cameraSetting.loadFile(fullPath);
});

ipcMain.on('s_message', (event, message) => {
    mainWin.webContents.send('r_message', message)
});

ipcMain.on('read_PF', (event, directoryPath) => {
    let peifangNameList = [];
    fs.readdir(directoryPath, (err, files) => {
        if (err) {
            console.error('读取文件夹出错:', err);
            return;
        }
        files.forEach((file) => {
            const filePath = path.join(directoryPath, file);
            let stats = fs.statSync(filePath)
            if (stats.isDirectory()) {
                peifangNameList.push(file); // 将文件夹名称添加到数组中
            }
        });
        event.sender.send('write_PF', peifangNameList)
    });

});

ipcMain.on('s_param', (event, Paramter,base64Image) => {
    var CameraID = Paramter.Setting.cameraID
    var PF_name = Paramter.Setting.PF_name
    const PF_Path = './PeiFang/' + CameraID + '/' + PF_name;
    const img_Path = PF_Path + "/"+Paramter.Setting.type +".bmp"
    console.log("11111111111111111111111111",Paramter.Setting.type)
    MarkPath = path.join(PF_Path,'Mark.json')
    ROIPath = path.join(PF_Path,'ROI.json')
    PointPath = path.join(PF_Path,'Point.json')
    ConfigPath = path.join(PF_Path,'Config.json')
    
    let temp_markw = Paramter.Mark.w
    let temp_markh = Paramter.Mark.h
    let temp_markx = Paramter.Mark.x
    let temp_marky = Paramter.Mark.y
    const imageBuffer = Buffer.from(base64Image.split(',')[1], 'base64');

    sharp(imageBuffer)
    .extract({ left: temp_markx, top: temp_marky, width: temp_markw, height: temp_markh })
    .toFile(img_Path, (err, info) => {
    if (err) {
      console.error('Error saving cropped image:', err);
    } else {
      console.log('Cropped image saved successfully:', info);
    }
  });

    fs.mkdir(PF_Path, { recursive: true }, (err) => {
        if (err) {
            console.error('创建目录失败:', err);
            return;
        }

        // 将JSON字符串写入文件
        fs.writeFile(MarkPath, JSON.stringify(Paramter.Mark), (err) => {
            if (err) {
                console.error('写入文件失败:', err);
                return;
            }
            console.log('JSON文件已保存:', MarkPath);
        });

        fs.writeFile(ROIPath, JSON.stringify(Paramter.ROI), (err) => {
            if (err) {
                console.error('写入文件失败:', err);
                return;
            }
            console.log('JSON文件已保存:', ROIPath);
        });

        fs.writeFile(PointPath, JSON.stringify(Paramter.Point), (err) => {
            if (err) {
                console.error('写入文件失败:', PointPath);
                return;
            }
            console.log('JSON文件已保存:', MarkPath);
        });

        fs.writeFile(ConfigPath, JSON.stringify(Paramter.Config), (err) => {
            if (err) {
                console.error('写入文件失败:', err);
                return;
            }
            console.log('JSON文件已保存:', ConfigPath);
        });
    });


});

ipcMain.on('send_product_type_param', (event, Paramter,path) => {
    const directoryPath = path; // 替换为你的目录路径
    const fileName = 'Product_type_parameters.json';
    const fullFilePath = directoryPath+"/" +fileName;
    console.log(fullFilePath)
    
    // 将JSON对象转换为字符串
    const jsonContent =Paramter
    
    // 确保目录存在，如果不存在则创建
    fs.mkdir(directoryPath, { recursive: true }, (err) => {
      if (err) {
        console.error('创建目录失败:', err);
        return;
      }
      
      // 将JSON字符串写入文件
      fs.writeFile(fullFilePath, jsonContent, (err) => {
        if (err) {
          console.error('写入文件失败:', err);
          return;
        }
        console.log('JSON文件已保存:', fullFilePath);
      });

    });


});

ipcMain.on('send_names', (event, cameranum,oldname,newname) => {
   console.log(cameranum,oldname,newname);
   let folder_path = "./PeiFang/"+cameranum
   let old_folder_path = path.join(folder_path, oldname); // 构建旧文件夹的完整路径
   let new_folder_path = path.join(folder_path, newname); // 构建新文件夹的完整路径
    // 重命名文件夹
   fs.rename(old_folder_path, new_folder_path, (err) => {
    if (err) {
       // 如果发生错误，打印错误信息
       console.error('Error renaming folder:', err);
       event.reply('rename_error', err.message);
    } else {
       // 如果重命名成功，打印成功信息
       console.log('Folder renamed successfully');
       event.reply('rename_success', newname);
    }
 });
});

app.on('ready', () => {
    createWindow()
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})