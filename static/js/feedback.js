/**
 * Created by eligah on 2016/3/30.
 */
$(function() {
    $("#cQuestion").bind("click", function () {
        $("#backBtn").replaceWith("<button class=\"btn\" id=\"backBtn\">疑问句</button>")
    })
    $("#cNegatives").bind("click", function () {
        $("#backBtn").replaceWith("<button class=\"btn\" id=\"backBtn\">否定句</button>")
    })
    $("#cState").bind("click", function () {
        $("#backBtn").replaceWith("<button class=\"btn\" id=\"backBtn\">陈述句</button>")
    })
})