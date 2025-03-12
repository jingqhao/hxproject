let index = 1;//配方个数
let current_double_click_name;
document.getElementById('workpiece_view').addEventListener('dblclick', () => {
  var current_camera_type = document.querySelector('#camera_switch select').options[document.querySelector('#camera_switch select').selectedIndex].text;
  if (current_camera_type == "进料相机") {
    foldername = "Camera1"
  } else if (current_camera_type == "对位相机1") {
    foldername = "Camera2"
  } else if (current_camera_type == "对位相机2") {
    foldername = "Camera3"
  } else {
    foldername = "Camera1"
  }
  var productName = document.getElementById('product_name').value;
  window.paramter.openNewWindow('pages/Search_module.html', foldername, productName, 'workpiece');
  // window.SM.snedSetting();
});

document.getElementById('target_view').addEventListener('dblclick', () => {
  var current_camera_type = document.querySelector('#camera_switch select').options[document.querySelector('#camera_switch select').selectedIndex].text;
  if (current_camera_type == "进料相机") {
    foldername = "Camera1"
  } else if (current_camera_type == "对位相机1") {
    foldername = "Camera2"
  } else if (current_camera_type == "对位相机2") {
    foldername = "Camera3"
  } else {
    foldername = "Camera1"
  }
  var productName = document.getElementById('product_name').value;
  window.paramter.openNewWindow('pages/Search_module.html', foldername, productName, 'target');
});

document.addEventListener('DOMContentLoaded', function () {
  var list = document.getElementById('PeifangList');
  var workpiece_div = document.getElementById('workpiece_view');
  var target_div = document.getElementById('target_view');
  // 获取输入框元素
  var productNameInput = document.getElementById('product_name');
  //双击标签内容实现切换
  list.addEventListener('dblclick', function (e) {
    if (e.target.tagName === 'LI') {
     
      var names = e.target.textContent.split('|')[1];
      var selectElement = document.querySelector('#camera_switch select');
      var current_camera_type = selectElement.options[selectElement.selectedIndex].text;
      var img_path = LoadData(current_camera_type, names)
      var workpiece_img_path = img_path.imagePath1
      var target_img_path = img_path.imagePath2
       // 清空之前的内容
       workpiece_div.innerHTML = '';
       target_div.innerHTML = '';
       current_double_click_name = names

      // 设置div的样式，使其背景为灰色并使用Flexbox布局
      workpiece_div.style.display = 'flex';
      workpiece_div.style.justifyContent = 'center'; // 水平居中
      workpiece_div.style.alignItems = 'center'; // 垂直居中
      workpiece_div.style.minHeight = '100px'; // 设置最小高度，根据需要调整
      workpiece_div.style.backgroundColor = '#808080'; // 设置背景色为灰色，可以使用任何灰色值

      target_div.style.display = 'flex';
      target_div.style.justifyContent = 'center';
      target_div.style.alignItems = 'center';
      target_div.style.minHeight = '100px';
      target_div.style.backgroundColor = '#808080';
      var rect1 = workpiece_div.getBoundingClientRect();
      var rect2 = target_div.getBoundingClientRect();
     

      var workpiece_pic = document.createElement('img');
      workpiece_pic.onload = function() {
        // 获取图像的宽度和高度
        var width = workpiece_pic.width;
        var height = workpiece_pic.height;
        // console.log("11111",width,height)
        // console.log("workpiece_div",rect1.width,rect1.height)
        // console.log("target_div",rect2.width,rect1.height)
        if ((width/height)>(rect1.width/rect1.height)) {
          workpiece_pic.style.width = '100%'; // 设置图片最大宽度为div的100%
          workpiece_pic.style.height = 'auto'; // 设置图片最大高度为div的100%
        } else {
          workpiece_pic.style.width = 'auto'; // 设置图片最大宽度为div的100%
          workpiece_pic.style.height = '100%'; // 设置图片最大高度为div的100%
        }
        workpiece_pic.style.objectFit = 'contain'; // 保持图片比例，不拉伸
        // 将图片添加到workpiece_div中
        workpiece_div.appendChild(workpiece_pic);
      };
      // 设置图片的src属性，这会触发加载过程(异步)

      var timestamp = new Date().getTime();
      workpiece_pic.src = `file://${workpiece_img_path}?${timestamp}`;
    
    //  workpiece_pic.src = `file://${workpiece_img_path}`;

      

      var target_pic = document.createElement('img');
      target_pic.onload = function() {
        // 获取图像的宽度和高度
        var width = target_pic.width;
        var height = target_pic.height;
        if ((width/ height)>(rect2.width/rect1.height)) {
          target_pic.style.width = '100%'; // 设置图片最大宽度为div的100%
          target_pic.style.height = 'auto'; // 设置图片最大高度为div的100%
        } else {
          target_pic.style.width = 'auto'; // 设置图片最大宽度为div的100%
          target_pic.style.height = '100%'; // 设置图片最大高度为div的100%
        }
        target_pic.style.objectFit = 'contain'; // 保持图片比例，不拉伸
        // 将图片添加到workpiece_div中
        target_div.appendChild(target_pic);
      };
       //target_pic.src = `file://${target_img_path}`; 
      target_pic.src = `file://${target_img_path}?${timestamp}`;
      //显示名字到右侧
      productNameInput.value = names;
    }
  });


  // 获取新增按钮元素
  var addButton = document.getElementById('add_new_peifang');
  const folderList = document.getElementById('PeifangList');
  addButton.addEventListener('click', function () {
    // 创建一个新的li元素
    var newListItem = document.createElement('li');
    var span = document.createElement('span');
    span.style.marginRight = '5px';
    span.textContent = index + ' |'; // 使用index变量作为索引号
    var separator = document.createElement('span');
    separator.textContent = 'default' + index; // 设置名称为"default"
    newListItem.appendChild(span);
    newListItem.appendChild(separator);
    folderList.appendChild(newListItem); // 将新的li元素添加到列表中


    // 清空之前的图像
    workpiece_div.innerHTML = '';
    target_div.innerHTML = '';
    productNameInput.value = 'default' + index;;
    index++; // 更新索引号
  });

});

function Load_and_Show_PeifangName(type) {
  let current_camera_type = type
  let foldername;
  let directoryPath;
  let peifang_name_list;

  if (current_camera_type == "进料相机") {
    foldername = "Camera1"
  } else if (current_camera_type == "对位相机1") {
    foldername = "Camera2"
  } else if (current_camera_type == "对位相机2") {
    foldername = "Camera3"
  } else {
    foldername = "Camera1"
  }

  directoryPath = "./PeiFang/" + foldername;
  window.PF.PF_load(directoryPath);

  return new Promise((resolve, reject) => {
    window.PF.PF_Write((event, peifang_name_list) => {
      resolve(peifang_name_list);
    });
  });
}

function LoadData(type, PF_name) {
  let current_camera_type = type;
  let peifang_name = PF_name;
  let foldername;

  if (current_camera_type == "进料相机") {
    foldername = "Camera1"
  } else if (current_camera_type == "对位相机1") {
    foldername = "Camera2"
  } else if (current_camera_type == "对位相机2") {
    foldername = "Camera3"
  } else {
    foldername = "Camera1"
  }

  //===================================读取图像
  let imagePath1, imagePath2;
  imagePath1 = "D:/UVP/code_set/HX/PeiFang/" + foldername + "/" + peifang_name + "/" + 'workpiece.bmp';
  imagePath2 = "D:/UVP/code_set/HX/PeiFang/" + foldername + "/" + peifang_name + "/" + 'target.bmp';
  return { imagePath1: imagePath1, imagePath2: imagePath2 };
}
function Load_Default_data() {
  var names = "abc";
  var selectElement = document.querySelector('#camera_switch select');
  var current_camera_type = selectElement.options[selectElement.selectedIndex].text;
  var img_path = LoadData(current_camera_type, names)
  var workpiece_img_path = img_path.imagePath1
  var target_img_path = img_path.imagePath2
  console.log("图像路径:", workpiece_img_path)
  var workpiece_div = document.getElementById('workpiece_view');
  var target_div = document.getElementById('target_view');


  // 设置div的样式，使其背景为灰色并使用Flexbox布局
  workpiece_div.style.display = 'flex';
  workpiece_div.style.justifyContent = 'center'; // 水平居中
  workpiece_div.style.alignItems = 'center'; // 垂直居中
  workpiece_div.style.minHeight = '100px'; // 设置最小高度，根据需要调整
  workpiece_div.style.backgroundColor = '#808080'; // 设置背景色为灰色，可以使用任何灰色值

  target_div.style.display = 'flex';
  target_div.style.justifyContent = 'center';
  target_div.style.alignItems = 'center';
  target_div.style.minHeight = '100px';
  target_div.style.backgroundColor = '#808080';

  // 清空之前的内容
  workpiece_div.innerHTML = '';
  target_div.innerHTML = '';

  var workpiece_pic = document.createElement('img');
  workpiece_pic.src = `file://${workpiece_img_path}`;
  workpiece_pic.style.width = '100%'; // 设置图片最大宽度为div的100%
  workpiece_pic.style.height = 'auto'; // 设置图片最大高度为div的100%
  workpiece_pic.style.objectFit = 'contain'; // 保持图片比例，不拉伸

  var target_pic = document.createElement('img');
  target_pic.src = `file://${target_img_path}`;
  target_pic.style.width = '100%';
  target_pic.style.height = 'auto';
  target_pic.style.objectFit = 'contain';

  workpiece_div.appendChild(workpiece_pic);
  target_div.appendChild(target_pic);

  //显示名字到右侧
  // 获取输入框元素
  var productNameInput = document.getElementById('product_name');
  productNameInput.value = names;
}

window.onload = function () {
  let peifang_name_list = []
  Load_and_Show_PeifangName("进料相机").then(res => {
    peifang_name_list = res;
    const folderList = document.getElementById('PeifangList');
    peifang_name_list.forEach(name => {
      const li = document.createElement('li');
      const span = document.createElement('span');
      span.style.marginRight = '5px';
      span.textContent = index + ' |';
      const separator = document.createElement('span');
      separator.textContent = name;
      li.appendChild(span);
      li.appendChild(separator);
      folderList.appendChild(li);
      index++;
    });
  });

  Load_Default_data();//页面加载,默认显示abc配方

}

document.addEventListener('DOMContentLoaded', function () {
  var currentEditableTd;
  var keyboard = document.getElementById('keyboard');

  // 双击事件，使 td 元素变为可编辑状态或选择框
  document.querySelectorAll('table td:not(:first-child)').forEach(function (td) {
    td.addEventListener('dblclick', function () {
      // 如果当前有可编辑的td，移除其可编辑状态
      if (currentEditableTd && currentEditableTd !== td) {
        currentEditableTd.classList.remove('editable');
        currentEditableTd.contentEditable = 'false';
        // 如果当前可编辑的td是选择框，恢复为文本
        if (currentEditableTd.firstChild && currentEditableTd.firstChild.tagName === 'SELECT') {
          currentEditableTd.innerHTML = currentEditableTd.firstChild.value;
          currentEditableTd.firstChild.remove();
        }
      }
      currentEditableTd = td;
      // 判断是否是特定的td
      if (td.id === 'point_to_point') {
        // 创建选择框并添加选项
        var select = document.createElement('select');
        select.innerHTML = '<option value="---">---</option> <option value="点对位">点对位</option><option value="非点对位">非点对位</option><option value="---">---</option> ';
        td.innerHTML = ''; // 清空td内容
        td.appendChild(select); // 添加选择框到td
        // 监听选择框的变化
        select.addEventListener('change', function () {
          // 更新td内容并移除选择框
          td.innerHTML = this.value;
          select.remove();
          keyboard.style.display = 'none'; // 隐藏键盘（如果有）
        });
      } else if (td.id === 'limit_axis_move') {
        // 创建选择框并添加选项
        var select = document.createElement('select');
        select.innerHTML = '<option value="---">---</option> <option value="是">是</option><option value="否">否</option> <option value="---">---</option>';
        td.innerHTML = ''; // 清空td内容
        td.appendChild(select); // 添加选择框到td
        // 监听选择框的变化
        select.addEventListener('change', function () {
          console.log(this.value); // 现在会正确打印“是”或“否”
          // 更新td内容并移除选择框
          td.innerHTML = this.value;
          select.remove();
          keyboard.style.display = 'none'; // 隐藏键盘（如果有）
        });
      } else if (td.id === 'limit_max_move_num') {
        // 创建选择框并添加选项
        var select = document.createElement('select');
        select.innerHTML = '<option value="---">---</option> <option value="是">是</option><option value="否">否</option> <option value="---">---</option>';
        td.innerHTML = ''; // 清空td内容
        td.appendChild(select); // 添加选择框到td
        // 监听选择框的变化
        select.addEventListener('change', function () {
          console.log(this.value); // 现在会正确打印“是”或“否”
          // 更新td内容并移除选择框
          td.innerHTML = this.value;
          select.remove();
          keyboard.style.display = 'none'; // 隐藏键盘（如果有）
        });
      } else if (td.id === 'x_axis_direction') {
        // 创建选择框并添加选项
        var select = document.createElement('select');
        select.innerHTML = '<option value="---">---</option> <option value="是">是</option><option value="否">否</option> <option value="---">---</option>';
        td.innerHTML = ''; // 清空td内容
        td.appendChild(select); // 添加选择框到td
        // 监听选择框的变化
        select.addEventListener('change', function () {
          console.log(this.value); // 现在会正确打印“是”或“否”
          // 更新td内容并移除选择框
          td.innerHTML = this.value;
          select.remove();
          keyboard.style.display = 'none'; // 隐藏键盘（如果有）
        });
      } else if (td.id === 'y_axis_direction') {
        // 创建选择框并添加选项
        var select = document.createElement('select');
        select.innerHTML = '<option value="---">---</option> <option value="是">是</option><option value="否">否</option> <option value="---">---</option>';
        td.innerHTML = ''; // 清空td内容
        td.appendChild(select); // 添加选择框到td
        // 监听选择框的变化
        select.addEventListener('change', function () {
          console.log(this.value); // 现在会正确打印“是”或“否”
          // 更新td内容并移除选择框
          td.innerHTML = this.value;
          select.remove();
          keyboard.style.display = 'none'; // 隐藏键盘（如果有）
        });
      } else if (td.id === 'q_axis_direction') {
        // 创建选择框并添加选项
        var select = document.createElement('select');
        select.innerHTML = '<option value="---">---</option> <option value="是">是</option><option value="否">否</option> <option value="---">---</option>';
        td.innerHTML = ''; // 清空td内容
        td.appendChild(select); // 添加选择框到td
        // 监听选择框的变化
        select.addEventListener('change', function () {
          console.log(this.value); // 现在会正确打印“是”或“否”
          // 更新td内容并移除选择框
          td.innerHTML = this.value;
          select.remove();
          keyboard.style.display = 'none'; // 隐藏键盘（如果有）
        });
      } else {
        // 其他td变为可编辑状态
        td.classList.add('editable');
        td.contentEditable = 'true';
        td.focus();
        keyboard.style.display = 'block';
      }
    });
  });


  // ==============================================数字键盘操作
  var num = "";
  let buttons = {
    '0': document.getElementById('num0'),
    '1': document.getElementById('num1'),
    '2': document.getElementById('num2'),
    '3': document.getElementById('num3'),
    '4': document.getElementById('num4'),
    '5': document.getElementById('num5'),
    '6': document.getElementById('num6'),
    '7': document.getElementById('num7'),
    '8': document.getElementById('num8'),
    '9': document.getElementById('num9')
  };

  Object.values(buttons).forEach(button => {
    button.addEventListener('click', () => {
      num += button.id.split('num')[1];

      if (currentEditableTd) {
        currentEditableTd.innerHTML = num; // 将num的值赋给当前可编辑的td元素
      }
    });
  });

  let del = document.getElementById('del');
  del.addEventListener('click', () => {
    num = num.slice(0, -1);
    if (currentEditableTd) {
      currentEditableTd.innerHTML = num; // 将num的值赋给当前可编辑的td元素
    }
  });

  let Enter = document.getElementById('Enter');
  Enter.addEventListener('click', () => {
    keyboard.style.display = 'none';

    if (currentEditableTd) {
      currentEditableTd.innerHTML = num; // 将num的值赋给当前可编辑的td元素
      num = ""; // 清空num以便下一次输入
      currentEditableTd.classList.remove('editable');
    }
  });

  let dot = document.getElementById('dot');
  dot.addEventListener('click', () => {
    num += ".";
    if (currentEditableTd) {
      currentEditableTd.innerHTML = num; // 将num的值赋给当前可编辑的td元素
    }
  });

  let clear = document.getElementById('clear');
  clear.addEventListener('click', () => {
    num = "";
    if (currentEditableTd) {
      currentEditableTd.innerHTML = num; // 将num的值赋给当前可编辑的td元素
    }
  });

  let minus_sign = document.getElementById('minus_sign');
  minus_sign.addEventListener('click', () => {
    num += "-";
    if (currentEditableTd) {
      currentEditableTd.innerHTML = num; // 将num的值赋给当前可编辑的td元素
    }
  });

});


document.addEventListener('DOMContentLoaded', function () {
  // 获取按钮元素
  var modifyButton = document.getElementById('modify');
  // 为按钮添加点击事件监听器
  modifyButton.addEventListener('click', function () {
    //先判断是否改变文件夹名字
    if(current_double_click_name!=document.getElementById('product_name').value){
      reName_Folder();
    }
    
    saveToJSON();
    //更新列表

    let peifang_name_list = []
    Load_and_Show_PeifangName("进料相机").then(res => {
      peifang_name_list = res;
      const folderList = document.getElementById('PeifangList');
      folderList.innerHTML = '';
      index = 1;
      peifang_name_list.forEach(name => {
        const li = document.createElement('li');
        const span = document.createElement('span');
        span.style.marginRight = '5px';
        span.textContent = index + ' |';
        const separator = document.createElement('span');
        separator.textContent = name;
        li.appendChild(span);
        li.appendChild(separator);
        folderList.appendChild(li);
        index++;
      });
    });
  
    

    // 弹出提示框
    alert('参数已修改并保存!');
  });
});

function saveToJSON() {
  // 创建一个空对象来存储数据
  let data = {
    对位参数: {},
    对位精度: {},
    目标补偿: {},
    最大移动量: {},
    出料补偿大小: {},
    方向取反: {}
  };

  // 获取所有的tr元素
  let rows = document.querySelectorAll('tbody tr');

  // 遍历每一行
  rows.forEach(function (row) {
    // 获取td元素
    let cells = row.querySelectorAll('td');
    if (cells.length === 2) {
      let key = cells[0].innerText; // 键是第一个td的文本内容
      let value = cells[1].innerText; // 值是第二个td的文本内容

      // 根据id将值分配到对应的JSON对象中
      switch (cells[1].id) {
        case 'point_to_point':
          data.对位参数['对位类型'] = value;
          break;
        case 'max-pairs':
          data.对位参数['最大对位次数'] = parseInt(value);
          break;
        case 'alignment_accuracy_x':
          data.对位精度['X轴方向(mm)'] = parseFloat(value);
          break;
        case 'alignment_accuracy_y':
          data.对位精度['Y轴方向(mm)'] = parseFloat(value);
          break;
        case 'alignment_accuracy_θ':
          data.对位精度['θ轴方向(度)'] = parseFloat(value);
          break;
        case 'target_compensation_x':
          data.目标补偿['X轴方向(mm)'] = parseFloat(value);
          break;
        case 'target_compensation_y':
          data.目标补偿['Y轴方向(mm)'] = parseFloat(value);
          break;
        case 'target_compensation_θ':
          data.目标补偿['θ轴方向(度)'] = parseFloat(value);
          break;
        case 'limit_max_move_num':
          data.最大移动量['限制最大移动量'] = value === '是' ? true : false;
          break;
        case 'limit_axis_move':
          data.最大移动量['限制轴移动量'] = value === '是' ? true : false;
          break;
        case 'max_move_x':
          data.最大移动量['X轴方向(mm)'] = parseFloat(value);
          break;
        case 'max_move_y':
          data.最大移动量['Y轴方向(mm)'] = parseFloat(value);
          break;
        case 'max_move_θ':
          data.最大移动量['θ轴方向(度)'] = parseFloat(value);
          break;
        case 'feed_compensation_x':
          data.出料补偿大小['X轴方向(mm)'] = parseFloat(value);
          break;
        case 'feed_compensation_y':
          data.出料补偿大小['Y轴方向(mm)'] = parseFloat(value);
          break;
        case 'feed_compensation_θ':
          data.出料补偿大小['θ轴方向(度)'] = parseFloat(value);
          break;
        case 'x_axis_direction':
          data.方向取反['X轴方向取反'] = value === '是' ? true : false;
          break;
        case 'y_axis_direction':
          data.方向取反['Y轴方向取反'] = value === '是' ? true : false;
          break;
        case 'q_axis_direction':
          data.方向取反['Q轴方向取反'] = value === '是' ? true : false;
          break;
      }
    }
  });

  // 将JSON对象转换为字符串
  let jsonString = JSON.stringify(data);
  var current_camera_type = document.querySelector('#camera_switch select').options[document.querySelector('#camera_switch select').selectedIndex].text;
  let foldername; 
  if (current_camera_type == "进料相机") {
    foldername = "Camera1"
  } else if (current_camera_type == "对位相机1") {
    foldername = "Camera2"
  } else if (current_camera_type == "对位相机2") {
    foldername = "Camera3"
  } else {
    foldername = "Camera1"
  }
  var productName = document.getElementById('product_name').value;
  let path = "./PeiFang/"+foldername+"/"+productName;

  window.Product_type_ParamSave.sendParam(jsonString,path)

  console.log(jsonString);

}

function reName_Folder(){
  var current_camera_type = document.querySelector('#camera_switch select').options[document.querySelector('#camera_switch select').selectedIndex].text;
  let foldername; 
  if (current_camera_type == "进料相机") {
    foldername = "Camera1"
  } else if (current_camera_type == "对位相机1") {
    foldername = "Camera2"
  } else if (current_camera_type == "对位相机2") {
    foldername = "Camera3"
  } else {
    foldername = "Camera1"
  }
  window.rename.sendParam(foldername,current_double_click_name,document.getElementById('product_name').value) 

}