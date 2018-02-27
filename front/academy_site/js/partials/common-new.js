//============================================   templaterTask


function templater(templateString, dataObj) {

    var resultStr = templateString.replace(/\${(.*?)\}/g, function (match, p1, p2, p3, offset, string){
        // if (!(dataObj[p1] == undefined)){
        //     p1 = dataObj[p1];
        // } else {
        //     p1 = 'none';
        // }
        return dataObj[p1];
    });

    return resultStr;
}


templater('${who} ${action} ${what} ${sooqa}', {
    who: 'mama',
    action: 'mila',
    what: 'ramu'
});




//================================== isInArray(arr)


function isInArray(arr) {
    var res = true;
    for (var i = 1; i <= arguments.length -1; i++){
        if (!(arr.indexOf(arguments[i]) !=-1)){
            res = false;
        }


        
    }
    return res;
}

isInArray([1, 2], 1, 2);


//================================== toArray(obj)


function toArray(obj) {
    return Array.prototype.slice.call(obj);
}

function someFunc() {
    var args = toArray(arguments);
}

someFunc(1,2,3,4);


//================================== closest(node, testFunc)




