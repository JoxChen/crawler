const CryptoJS = require("crypto-js");

var f = {
    "-.": "a",
    ".---": "b",
    ".-.-": "c",
    ".--": "d",
    "--..": "e",
    "--.-": "f",
    "..-": "g",
    "----": "h",
    "--": "i",
    "-...": "j",
    ".-.": "k",
    "-.--": "l",
    "..": "m",
    ".-": "n",
    "...": "o",
    "-..-": "p",
    "..-.": "q",
    "-.-": "r",
    "---": "s",
    ".": "t",
    "--.": "u",
    "---.": "v",
    "-..": "w",
    ".--.": "x",
    ".-..": "y",
    "..--": "z",
    ".....": "0",
    "-....": "1",
    "--...": "2",
    "---..": "3",
    "----.": "4",
    "-----": "5",
    ".----": "6",
    "..---": "7",
    "...--": "8",
    "....-": "9",
    "-": "-"
}

var l = function (e) {
    var t = e.split("_").map((function (e) {
            return f[e]
        }
    ));
    return t.join("")
};

function de(e) {
    var t = l("-.-_--.._-.._--_.-_-_---_-.._----_.-.._---_.-.-_-...._--..._---.._----.")
        , n = CryptoJS.enc.Utf8.parse(t)
        , r = CryptoJS.AES.decrypt(e, n, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    });
    return CryptoJS.enc.Utf8.stringify(r).toString()
}

