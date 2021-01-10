// Show currency exchange form or funding form based on toggle
// Default funding form shown first
$("#form-type").change(function() {
    $(".currency-exchange-form").toggleClass("hide");
    $(".funding-form").toggleClass("hide");
})


// Show different label on form based on currency exchange direction
$("#exchange-direction").change(function() {
    let direction = $(this).val();
    if (direction === "SGD to USD") {
        $("#exchange-first-label").html("SGD");
        $("#exchange-second-label").html("USD");
        $("#exchange-first-name").attr("name", "sgd");
        $("#exchange-second-name").attr("name", "usd");
    } else {
        $("#exchange-first-label").html("USD");
        $("#exchange-second-label").html("SGD");
        $("#exchange-first-name").attr("name", "usd");
        $("#exchange-second-name").attr("name", "sgd");
    }
})