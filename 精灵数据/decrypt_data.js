const CryptoJS = require("crypto-js");


var j = "DXZWdxUZ5jgsUFPF"
    , z = CryptoJS.enc.Utf8.parse(j);

function de_data(data) {
    var e = CryptoJS.AES.decrypt(data, z, {
        iv: CryptoJS.enc.Utf8.parse(j.substr(0, 16)),
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    });
    return JSON.parse(e.toString(CryptoJS.enc.Utf8))
}
