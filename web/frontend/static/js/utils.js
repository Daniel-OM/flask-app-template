
function triggerChange(element) {
    element.dispatchEvent(new Event('change', { bubbles: true }));
}

function triggerInput(element) {
    element.dispatchEvent(new Event('input', { bubbles: true }));
}


async function post(url, data=null, callback=() => {}, files=[]) {
    console.log(data);
    $.ajax({
        type: 'POST',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('User', true);
        },
        url: url,
        contentType: 'application/json',
        data: JSON.stringify(data),
        files: files,
        dataType: 'json',
        success: function (response) {
            if (response.executed) {
                if (callback != null)
                    callback(response.data);
            } else {
                alert(response.description);
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.responseText, thrownError, 'error');
        }
    });
};

async function get(url, callback=() => {}, params=null) {

    if (params != null & false) {
        url += '?';
        let c = 0;
        for (const [key, value] of Object.entries(params)) {
            if (c > 0)
                url += '&';
            url += `${key}=${value}`;
        }
    }
    
    $.ajax({
        type: 'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('User', true);
        },
        url: url,
        data: params,
        success: function (response) {
            if (response.executed) {
                callback(response.data);
            } else {
                alert(response.description);
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.status, thrownError, 'error');
        }
    });
};

async function submitForm(id, url, change_select=true, submit=false, func=() => {}) {

    let form = document.getElementById(id);
    if (checkPasswords('password', 'pass_confirm')) {
        
        if (change_select) {
            form.getElementsByTagName('select').forEach(function (select) {
                let input = document.createElement('input');
                input.name = select.id;
                input.value = select.value;
                form.appendChild(input);
            });
            // Select2
            form.querySelectorAll('select.select2').forEach(function (select) {
                let input = document.createElement('input');
                input.name = select.id;
                input.value = select.value;
                form.appendChild(input);
            });
        }
        
        if (submit) {
            form.action = url;
            form.method = 'post';
            form.submit();
            form.action = '';
        } else {
            console.log('We are in a post');
            let formData = new FormData(form);
            var object = {};
            formData.forEach(function(value, key){
                object[key] = value;
            });
            console.log(object);
            await post(url, object, func);
        }
    }
}

function setCookie(name, value) {
    document.cookie = `${name}=${value}`;
}

function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) 
        return parts.pop().split(';').shift();
    else
        return null;
}

function setLocalStorage(name, value) {
    localStorage.setItem(name, value);
}

function getLocalStorage(name) {
    return localStorage.getItem(name);
}

function capitalize (string) {
    const words = string.split(" ");

    for (let i = 0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].substr(1);
    }

    return words.join(" ");
}
