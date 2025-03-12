const ws = new WebSocket("ws://localhost:9999/handler");

ws.onclose = function () {
    ws.send(JSON.stringify({ type: "Close" }));
    console.log("Websockets链接关闭");
};

window.onload = function () {
    let All_Paramter = { "ROI": {}, "Mark": {}, "Point": {}, "Setting": {}, "Config": {}, "Pic": {} }
    const query = new URLSearchParams(window.location.search);
    const cameraID = query.get("cameraID");
    const PF_name = query.get("peifang_name");
    const type = query.get("type");

    All_Paramter.Setting = { cameraID: cameraID, PF_name: PF_name, type: type }

    // 获取左侧按钮按钮
    const imgSaveBtn = document.getElementById('img_save');
    const drawRoiBtn = document.getElementById('draw_roi');
    const drawMarkBtn = document.getElementById('draw_mark');
    const clearRoiBtn = document.getElementById('clear_roi');
    const clearMarkBtn = document.getElementById('clear_mark');
    const confirmRoiMarkBtn = document.getElementById('comfirm_roi_mark');

    // 获取右侧上面按钮
    const loadImgBtn = document.getElementById('load_img');
    const loadCameraimgBtn = document.getElementById('load_img_from_Camera');
    const updatebtn = document.getElementById('update_img');
    const drawPointBtn = document.getElementById('draw_point');
    const clearPointBtn = document.getElementById('clear_point');
    const confirmPointBtn = document.getElementById('confirm_point');

    //获取参数按钮
    const saveParameterBtn = document.getElementById('save_parameter');
    // 获取画布

    const photoCanvas = document.getElementById('photoCanvas');
    const imageCanvas = document.getElementById('imageCanvas');
    const ctx = photoCanvas.getContext('2d');
    const ctx2 = imageCanvas.getContext('2d');

    // 画布宽高
    photoCanvas.width = 640;
    photoCanvas.height = 640;
    imageCanvas.width = 340;
    imageCanvas.height = 340;// var myCanvas_rect = photoCanvas.getBoundingClientRect();

    let base64Image;

    const photoWidth = photoCanvas.width;
    const photoHeight = photoCanvas.height;

    const imgWidth = imageCanvas.width;
    const imgHeight = imageCanvas.height;
    let temp_markw, temp_markh, temp_markx, temp_marky;



    // 初始图像数据
    let image = null;
    let originalImage = null; // 保存原始图像用于截取
    let currentAction = null; // 当前绘制动作
    let shapes = {}; // 保存绘制的矩形和点信息
    let tempShape = null; // 临时绘制的矩形

    let current_draw_canvas = "canvas1";
    let markX, markY, markW, markH;
    let scale_orange;
    let scale_point;
    //初始化相关按钮============================================================================
    // 初始化按钮状态
    setButtonStates({ loadImg: true });

    // 设置按钮状态
    function setButtonStates({ loadImg, imgsave, drawRoi, drawMark, drawPoint, clear_roi, clear_mark, clear_point, confirmRoiMark, confirmPoint }) {
        loadImgBtn.disabled = !loadImg;
        loadCameraimgBtn.disabled = !loadImg;

        drawRoiBtn.disabled = !drawRoi;
        imgSaveBtn.disabled = !imgsave;
        drawMarkBtn.disabled = !drawMark;
        drawPointBtn.disabled = !drawPoint;

        clearRoiBtn.disabled = !clear_roi;
        clearMarkBtn.disabled = !clear_mark;
        clearPointBtn.disabled = !clear_point;
        confirmPointBtn.disabled = !confirmPoint;
        confirmRoiMarkBtn.disabled = !confirmRoiMark;
    }

    // 加载图像
    loadImgBtn.addEventListener('click', function () {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = function (e) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = function (event) {
                const img = new Image();
                img.onload = function (event) {
                    originalImage = img;
                    // 保存原始图像尺寸
                    const originalWidth = img.width;
                    const originalHeight = img.height;
                    // 计算缩放比例
                    if (originalWidth > originalHeight) {
                        // 图像宽度大于高度，让图像宽度占满画布
                        scale_orange = photoWidth / originalWidth;
                    } else {
                        // 图像高度大于宽度，让图像高度占满画布
                        scale_orange = photoHeight / originalHeight;
                    }
                    // 计算新的图像尺寸
                    const newWidth = originalWidth * scale_orange;
                    const newHeight = originalHeight * scale_orange;
                    // 清除画布
                    ctx.clearRect(0, 0, photoWidth, photoHeight);
                    // 绘制图像，使其居中显示
                    ctx.drawImage(
                        img,
                        (photoWidth - newWidth) / 2, // x 坐标偏移量以居中
                        (photoHeight - newHeight) / 2, // y 坐标偏移量以居中
                        newWidth,
                        newHeight
                    );

                    image = img;
                    setButtonStates({ loadImg: true, imgsave: true, drawRoi: true, drawMark: true, clear_roi: true, clear_mark: true, confirmRoiMark: true });
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        };
        input.click();
    });
    //同步摄像头画面
    loadCameraimgBtn.addEventListener('click', function () {
        if (cameraID == "Camera1") {
            ws.send(JSON.stringify({ type: "UpdateModeImg1" }));
        } else if (cameraID == "Camera1") {
            ws.send(JSON.stringify({ type: "UpdateModeImg2" }));
        } else {
            ws.send(JSON.stringify({ type: "UpdateModeImg3" }));
        }

    });

    //收到画面进行更新
    ws.onmessage = function (evt) {
        console.log("2---------------------------------")
        var Port_connect, received_msg = evt.data;
        const data = JSON.parse(received_msg);
        console.log("data", data);
        const data1 = data[0];
        const frameName = data1.frame_name;
        console.log("frameName", frameName);
        const imgData = `data:image/jpeg;base64,${data1.img_data}`;

        const img = new Image();
        img.onload = function () {
            // 保存原始图像尺寸
            const originalWidth = img.width;
            const originalHeight = img.height;
            // 计算缩放比例
            const scale_orange = Math.min(photoWidth / originalWidth, photoHeight / originalHeight);
            // 计算新的图像尺寸
            const newWidth = originalWidth * scale_orange;
            const newHeight = originalHeight * scale_orange;
            // 清除画布
            ctx.clearRect(0, 0, photoWidth, photoHeight);
            // 绘制图像，使其居中显示
            ctx.drawImage(
                img,
                (photoWidth - newWidth) / 2, // x 坐标偏移量以居中
                (photoHeight - newHeight) / 2, // y 坐标偏移量以居中
                newWidth,
                newHeight
            );
            // 图像已经加载并绘制完成，你可以在这里设置其他的状态或回调
        };

        // 设置 Image 对象的 src 属性为 Base64 编码的字符串
        img.src = imgData;
        originalImage = img;
        image = img;
        setButtonStates({ loadImg: true, imgsave: true, drawRoi: true, drawMark: true, clear_roi: true, clear_mark: true, confirmRoiMark: true });

    };

    //更新画面
    updatebtn.addEventListener('click', function () {
        if (cameraID == "Camera1") {
            ws.send(JSON.stringify({ type: "UpdateModeImg1" }));
        } else if (cameraID == "Camera1") {
            ws.send(JSON.stringify({ type: "UpdateModeImg2" }));
        } else {
            ws.send(JSON.stringify({ type: "UpdateModeImg3" }));
        }

    });
    //图像保存，似乎目前不能设置路径和名字
    imgSaveBtn.addEventListener('click', function () {
        if (!originalImage) {
            alert('No image loaded!');
            return;
        }

        // 创建一个临时画布
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        // 设置画布的大小为原始图像的大小
        canvas.width = originalImage.width;
        canvas.height = originalImage.height;
        // 在画布上绘制原始图像
        ctx.drawImage(originalImage, 0, 0);
        // 将画布内容转换为数据URL (PNG格式)
        const dataURL = canvas.toDataURL('image/png');

        // 创建一个<a>元素用于下载
        const link = document.createElement('a');
        link.href = dataURL;

        // 使用时间戳作为文件名
        const timestamp = new Date().getTime();
        link.download = `image_${timestamp}.png`;

        // 触发链接点击以开始下载
        link.click();

    });
    //时间绑定===============================================================================
    //绘画按钮事件绑定
    drawRoiBtn.addEventListener('click', function () {
        currentAction = 'draw_roi';

        startDrawingRect('rect');
    });
    drawMarkBtn.addEventListener('click', function () {
        currentAction = 'draw_mark';
        startDrawingRect('rect');
    });
    drawPointBtn.addEventListener('click', function () {
        currentAction = 'draw_point';
        startDrawingPoint('point');
    });
    //清除按钮事件绑定
    clearRoiBtn.addEventListener('click', function () {
        currentAction = 'draw_roi';

        clearCurrentShape('draw_roi');
    });
    clearMarkBtn.addEventListener('click', function () {
        currentAction = 'draw_mark';
        clearCurrentShape('draw_mark');
    });
    clearPointBtn.addEventListener('click', function () {
        currentAction = 'draw_point';
        clearCurrentShape('draw_point');
    });

    //确认按钮事件绑定
    confirmRoiMarkBtn.addEventListener('click', function () {
        currentAction = 'confirm_roi_mark';
        current_draw_canvas = "canvas2";//确定之后表示转到绘制画布2
        confirmAction('confirm_roi_mark');
    });
    confirmPointBtn.addEventListener('click', function () {
        currentAction = 'confirm_point';
        current_draw_canvas = "canvas1"//确定之后表示转到绘制画布1
        confirmAction('confirm_point');
    });

    saveParameterBtn.addEventListener('click', function () {
        getParameters();//获取参数
        alert('配方已保存到: ' + PF_name);
        window.close();//关闭页面
    });

    //相关函数实现==============================================================================
    // 清除当前图形
    function clearCurrentShape(currentShape) {

        if (currentShape == "draw_point") {
            delete shapes['points'];
            redrawImageCanvas();
        } else if (shapes[currentShape]) {
            delete shapes[currentShape];
            redrawCanvas();
        }
    }
    // 绘制矩形逻辑
    function startDrawingRect(drawType) {
        if (current_draw_canvas == "canvas1") {
            let isDrawing = false;
            let startX, startY;
            photoCanvas.onmousedown = function (e) {
                isDrawing = true;
                startX = e.offsetX;
                startY = e.offsetY;
                tempShape = null;
            };
            photoCanvas.onmousemove = function (e) {
                if (!isDrawing) return;
                const mouseX = e.offsetX;
                const mouseY = e.offsetY;
                if (drawType === 'rect') {
                    const width = mouseX - startX;
                    const height = mouseY - startY;
                    tempShape = { x: startX, y: startY, width, height };
                    redrawCanvas();
                    ctx.strokeStyle = currentAction.includes('roi') ? 'red' : 'green';
                    ctx.strokeRect(tempShape.x, tempShape.y, tempShape.width, tempShape.height);
                }
            };
            photoCanvas.onmouseup = function (e) {
                if (!isDrawing) return;
                isDrawing = false;
                if (drawType === 'rect' && tempShape) {
                    shapes[currentAction] = tempShape;
                    redrawCanvas();
                    drawLabel(currentAction);
                }
            };
        }

    }
    function startDrawingPoint(drawType) {
        imageCanvas.onmouseup = function (e) {
            if (drawType == 'point') {
                const point = { x: e.offsetX, y: e.offsetY };
                if (!shapes['points']) shapes['points'] = [];
                if (shapes['points'].length < 1) {
                    shapes['points'].push(point);
                    redrawImageCanvas();
                }

            }
        };
    }
    // 绘制标签
    function drawLabel(action) {
        const shape = shapes[action];
        if (shape) {
            ctx.font = '16px Arial';
            ctx.fillStyle = action.includes('roi') ? 'red' : 'green';
            let labelText = '';
            switch (action) {
                case 'draw_roi':
                    labelText = 'ROI';
                    break;
                case 'draw_mark':
                    labelText = 'MARK';
                    break;
            }
            ctx.fillText(labelText, shape.x + 5, shape.y + 20);
        } else if (action === 'draw_point' && shapes['points']) {
            ctx2.fillStyle = 'blue';
            shapes['points'].forEach((point, index) => {
                ctx2.beginPath();
                ctx2.arc(point.x, point.y, 5, 0, Math.PI * 2);
                ctx2.fill();
                ctx2.fillText(`基准点${index + 1}`, point.x + 10, point.y);
            });
        }
    }

    // 重绘矩形画布
    function redrawCanvas() {

        // 保存原始图像尺寸
        const originalWidth = image.width;
        const originalHeight = image.height;

        // 计算缩放比例
        if (originalWidth > originalHeight) {
            // 图像宽度大于高度，让图像宽度占满画布
            scale_orange = photoWidth / originalWidth;
        } else {
            // 图像高度大于宽度，让图像高度占满画布
            scale_orange = photoHeight / originalHeight;
        }

        // 计算新的图像尺寸
        const newWidth = originalWidth * scale_orange;
        const newHeight = originalHeight * scale_orange;

        // 清除画布
        ctx.clearRect(0, 0, photoWidth, photoHeight);

        // 绘制图像，使其居中显示
        ctx.drawImage(
            image,
            (photoWidth - newWidth) / 2, // x 坐标偏移量以居中
            (photoHeight - newHeight) / 2, // y 坐标偏移量以居中
            newWidth,
            newHeight
        );

        for (const key in shapes) {
            const shape = shapes[key];
            if (key !== 'points' && shape) {
                ctx.strokeStyle = key.includes('roi') ? 'red' : 'green';
                ctx.strokeRect(shape.x, shape.y, shape.width, shape.height);
                drawLabel(key);
            }
        }
    }
    // 重绘圆点画布
    function redrawImageCanvas() {


        imageCanvas.width = 340;  // 根据样式的宽度
        imageCanvas.height = 340; // 根据样式的高度

        if (temp_markw > temp_markh) {
            scale_point = 340 / temp_markw;
        } else {
            scale_point = 340 / temp_markh;
        }
        const newWidth = temp_markw * scale_point;
        const newHeight = temp_markh * scale_point;
        // 计算绘制时的起始X和Y坐标，以保持图像居中
        const startX = (340 - newWidth) / 2;
        const startY = (340 - newHeight) / 2;


        ctx2.clearRect(0, 0, 340, 340);

        // 绘制图像
        ctx2.drawImage(originalImage, temp_markx, temp_marky, temp_markw, temp_markh, startX, startY, newWidth, newHeight);
        for (const key in shapes) {
            const shape = shapes[key];

            if (key == 'points' && shape) {
                ctx2.fillStyle = 'green';
                shape.forEach((point, index) => {
                    ctx2.beginPath();
                    ctx2.arc(point.x, point.y, 5, 0, Math.PI * 2);


                    ctx2.strokeStyle = 'red'; // 设置线条颜色
                    ctx2.lineWidth = 2; // 设置线条宽度
                    ctx2.setLineDash([5, 5]); // 设置虚线模式

                    // 绘制垂直线
                    ctx2.moveTo(point.x, point.y);
                    ctx2.lineTo(point.x, point.y - 100);
                    ctx2.moveTo(point.x, point.y);
                    ctx2.lineTo(point.x, point.y + 100);

                    // 绘制水平线
                    ctx2.moveTo(point.x, point.y);
                    ctx2.lineTo(point.x + 100, point.y);
                    ctx2.moveTo(point.x, point.y);
                    ctx2.lineTo(point.x - 100, point.y);

                    ctx2.stroke(); // 绘制线条

                    ctx2.fill();
                    ctx2.fillText(`基准点${index + 1}`, point.x + 10, point.y);


                });
            }
        }
    }
    // 点击确认按钮后切换按钮状态并更新当前操作
    function confirmAction() {
        if (currentAction === 'confirm_roi_mark') {
            if (!shapes['draw_roi']) {
                alert('还没有进行绘制ROI！');
                current_draw_canvas = "canvas1"
                return;
            } else if (!shapes['draw_mark']) {
                alert('还没有进行绘制MARK！');
                current_draw_canvas = "canvas1"
                return;
            }

            // 计算原图与canvas的比例
            let scales;
            let x_bias = 0, y_bias = 0;

            if (originalImage.width > originalImage.height) {
                scales = originalImage.width / 640;
                y_bias = (640 - originalImage.height / scales);
            } else {
                scales = originalImage.height / 640;
                x_bias = (640 - originalImage.width / scales);
            }



            console.log("y_bias", y_bias);
            //原始大小
            let ROIX = shapes['draw_roi'].x * scales - x_bias;
            let ROIY = shapes['draw_roi'].y * scales - y_bias;
            let ROIW = shapes['draw_roi'].width * scales;
            let ROIH = shapes['draw_roi'].height * scales;

            let markX = shapes['draw_mark'].x * scales - x_bias;
            let markY = shapes['draw_mark'].y * scales - y_bias;
            let markW = shapes['draw_mark'].width * scales;
            let markH = shapes['draw_mark'].height * scales;

            temp_markw = markW;
            temp_markh = markH;
            temp_markx = markX;
            temp_marky = markY;

            //模板相对于ROI大小
            let relativeMarkX = shapes['draw_mark'].x * scales - ROIX;
            let relativeMarkY = shapes['draw_mark'].y * scales - ROIY;
            let relativeMarkW = shapes['draw_mark'].width * scales;
            let relativeMarkH = shapes['draw_mark'].height * scales;
            //判断MARK大小是否超过ROI

            if (markY < ROIY || markX < ROIX) {
                alert('MARK超出范围');
                current_draw_canvas = "canvas1"
                return;
            } else if (markW > ROIW || markH > ROIH) {
                alert('MARK超出范围');
                current_draw_canvas = "canvas1"
                return;
            } else if (markX + markW > ROIX + ROIW || markY + markH > ROIY + ROIH) {
                alert('MARK超出范围');
                current_draw_canvas = "canvas1"
                return;
            }

            //点击确认后打印ROI,保存mark图像
            All_Paramter.ROI = { x: ROIX, y: ROIY, w: ROIW, h: ROIH }
            All_Paramter.Mark = { x: markX, y: markY, w: markW, h: markH }
            console.log("ROI在原图坐标:", { x: ROIX, y: ROIY, w: ROIW, h: ROIH });
            console.log("MARK在原图坐标:", { x: markX, y: markY, w: markW, h: markH });
            console.log("MARK在ROI坐标:", { x: relativeMarkX, y: relativeMarkY, w: relativeMarkW, h: relativeMarkH });
            //先清空基准点，符合条件后，截取mark显示在画布2上
            clearCurrentShape('draw_point');
            extractModeImages();
            //取消左侧画布事件绑定
            photoCanvas.onmouseup = null;
            photoCanvas.onmousedown = null;
            photoCanvas.onmousemove = null;

        } else if (currentAction === 'confirm_point') {
            if (!shapes['points']) {
                alert('还没有进行绘制基准点！');
                current_draw_canvas = "canvas2"
                return;
            }

            //分两种情况来计算点在mark中的位置初步得到的点只是在画布上的位置
            let scale;
            let x_bias, y_bias;
            let right_x, right_y;
            if (temp_markw > temp_markh) {
                scale = temp_markw / 340;
                y_bias = (340 - temp_markh / scale) / 2
                right_y = (shapes['points'][0].y - y_bias) / scale;
                right_x = shapes['points'][0].x / scale;
            } else {
                scale = temp_markh / 340;
                x_bias = (340 - temp_markw / scale) / 2
                right_x = (shapes['points'][0].x - x_bias) * scale;
                right_y = shapes['points'][0].y * scale;
            }

            All_Paramter.Point = { x: right_x, y: right_y }
            console.log("points相对于ROI的坐标:", { x: right_x, y: right_y });
            //取消侧画布事件绑定
            imageCanvas.onmouseup = null;
            imageCanvas.onmousedown = null;
            imageCanvas.onmousemove = null;
            //恢复左侧按钮可按，右侧不可按，以便重新绘制
            setButtonStates({ loadImg: true, imgsave: true, drawRoi: true, drawMark: true, clear_roi: true, clear_mark: true, confirmRoiMark: true });

        }

    }

    // 截取原图显示在子画布
    function extractModeImages() {
        const MARK = shapes['draw_mark'];


        imageCanvas.width = 340;  // 根据样式的宽度
        imageCanvas.height = 340; // 根据样式的高度

        if (temp_markw > temp_markh) {
            scale_point = 340 / temp_markw;
        } else {
            scale_point = 340 / temp_markh;
        }
        const newWidth = temp_markw * scale_point;
        const newHeight = temp_markh * scale_point;
        // 计算绘制时的起始X和Y坐标，以保持图像居中
        const startX = (340 - newWidth) / 2;
        const startY = (340 - newHeight) / 2;


        ctx2.clearRect(0, 0, 340, 340);

        // 绘制图像
        ctx2.drawImage(originalImage, temp_markx, temp_marky, temp_markw, temp_markh, startX, startY, newWidth, newHeight);

        //设置基准点绘制按钮可按
        setButtonStates({ loadImg: true, drawPoint: true, clear_point: true, confirmPoint: true });

    }

    function getParameters() {
        // 获取 input 元素
        var score_value = document.getElementById('score_value').value;
        var min_angle = document.getElementById('min_angle').value;
        var max_angle = document.getElementById('max_angle').value;
        var tiers = document.getElementById('tiers').value;
        var step = document.getElementById('steps').value;
        All_Paramter.Config = { "score_value": score_value, "min_angle": min_angle, "max_angle": max_angle, "tiers": tiers, "step": step }

        const canvas1 = document.createElement('canvas');
        const ctx1 = canvas1.getContext('2d');
        canvas1.width = originalImage.width;
        canvas1.height = originalImage.height;
        ctx1.drawImage(originalImage, 0, 0);

        // 将 canvas 内容转换为 Base64 编码的图像数据
        const base64Image = canvas1.toDataURL('image/png');

        window.ParamSave.sendParam(All_Paramter, base64Image)
    }
};