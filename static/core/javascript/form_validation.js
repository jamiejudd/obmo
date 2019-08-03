//OLD VERSION OF TRANSFER 
  const fromHexString = hexString =>
    new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
  const toHexString = bytes =>
    bytes.reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');

  function validHex(string) {
    return (toHexString(fromHexString(string)) === string.toLowerCase()) ;
  }
  function validPubKey(string) {
    return (validHex(string) && string.length == 64) ;
  }
  /*
  function toHexStringz(byteArray) {
    return Array.prototype.map.call(byteArray, function(byte) {
      return ('0' + (byte & 0xFF).toString(16)).slice(-2);
    }).join('');
  }
  function toByteArrayz(hexString) {
    var result = [];
    while (hexString.length >= 2) {
      result.push(parseInt(hexString.substring(0, 2), 16));
      hexString = hexString.substring(2, hexString.length);
    }
    return result;
  }  
   */
  var fields = {}

  var Sender,
      SeqNo,
      Recipient,
      Amount,
      RawTxnString,
      RawTxnByteArray,
      //RawTxnHex,
      //SecretKey,
      //Keypair,
      Signature;

  function updateRawTxn() {
    Sender =  $("#id_sender").val();
    SeqNo =  $("#id_sender_seq_no").val();
    Recipient =  $("#id_recipient").val();
    Amount =  $("#id_amount").val();
    //RawTxnString = '{"Type":"Transfer","Sender":"'+Sender+'","SeqNo":'+SeqNo+',"Recipient":"'+Recipient+'","Amount":'+Amount+'}';
    RawTxnString = 'Type:Transfer,Sender:'+Sender+'","SeqNo":'+SeqNo+',"Recipient":"'+Recipient+'","Amount":'+Amount+'}';
    //RawTxnByteArray = new TextEncoder("utf-8").encode(RawTxnString);
    RawTxnString = 'Type:Transfer,Sender:'+ $("#id_sender").val() +',SeqNo:'+ String($("#id_sender_seq_no").val()) +',Recipient:'+ $("#id_recipient").val() +',Amount:'+ String($("#id_amount").val())
    $('#rawtxnstring').val(RawTxnString);
    $('#modalrawtxn').val(RawTxnString);
  }

  function checkSender() {
    Sender =  $("#id_sender").val();
    var is_valid = true;
    if( !Sender || Sender == "" ){
      $('#id_sender_feedback').text('This field is required.');
      $("#id_sender").addClass("is-invalid");
      is_valid = false;
    } else if(!validPubKey(Sender)){
      $('#id_sender_feedback').text('Not a valid public key.');
      //$(this).addClass("is-invalid");
      $("#id_sender").addClass("is-invalid");
      is_valid = false;
    } else {
      $("#id_sender").removeClass("is-invalid");
    }
    return is_valid;
  }

  function checkSeqNo() {
    SeqNo =  $("#id_sender_seq_no").val();
    var is_valid = true;
    if( !SeqNo || SeqNo == "" ){
      $('#id_sender_seq_no_feedback').text('This field is required.');
      $("#id_sender_seq_no").addClass("is-invalid");
      is_valid = false;
    } else if(!(SeqNo >= 1)){        //!( Number.isInteger($(this).val())
      $('#id_sender_seq_no_feedback').text('Must be a positive number.');
      $("#id_sender_seq_no").addClass("is-invalid");
      is_valid = false;
    } else {
      $("#id_sender_seq_no").removeClass("is-invalid");
    }
    return is_valid;
  }

  function checkRecipient() {
    Recipient =  $("#id_recipient").val();
    var is_valid = true;
    if( !Recipient || Recipient == "" ){
      $('#id_recipient_feedback').text('This field is required.');
      $("#id_recipient").addClass("is-invalid");
      is_valid = false;
    } else if(!validPubKey(Recipient)){
      $('#id_recipient_feedback').text('Not a valid public key.');
      $("#id_recipient").addClass("is-invalid");
      is_valid = false;
    } else if(Recipient == Sender){
      $('#id_recipient_feedback').text('Recipient cannot be same as sender.');
      $("#id_recipient").addClass("is-invalid");
      is_valid = false;
    } else {
      $("#id_recipient").removeClass("is-invalid");
    }
    return is_valid;
  }

  function checkAmount() {
    Amount =  $("#id_amount").val();
    var is_valid = true;
    if( !Amount || Amount == "" ){
      $('#id_amount_feedback').text('This field is required.');
      $("#id_amount").addClass("is-invalid");
      is_valid = false;
    } else if(!(200000000 >= Amount >= 1)){
      $('#id_amount_feedback').text('Must be a between 1 and 20000000.');
      $("#id_amount").addClass("is-invalid");
      is_valid = false;
    } else {
      $("#id_amount").removeClass("is-invalid");
    }
    return is_valid;
  }

  function checkFields() {
    var is_valid = true;
    is_valid = checkSender() && is_valid;
    is_valid = checkSeqNo() && is_valid;
    is_valid = checkRecipient() && is_valid;
    is_valid = checkAmount() && is_valid;
    return is_valid;
  }

  function checkSignature() {
    updateRawTxn()
    RawTxnByteArray = new TextEncoder("utf-8").encode(RawTxnString);
    Signature = document.getElementById("id_signature").value;
    try {
      if(nacl.sign.detached.verify( RawTxnByteArray, fromHexString(Signature), fromHexString(Sender))){
        $("#id_signature").removeClass("is-invalid");
        $("#id_signature").addClass("is-valid");
        return true;
      } else {
        $("#id_signature").removeClass("is-valid");
        $("#id_signature").addClass("is-invalid");
        return false;
      }
    } catch(e) {
      //console.log('sig error')
      //console.log(e.message)
      $("#id_signature").removeClass("is-valid");
      $("#id_signature").addClass("is-invalid");
      return false;
    }
  }


  $("#id_txn_type,#id_sender,#id_sender_seq_no,#id_recipient,#id_amount").on("change paste keyup input", function() {
    updateRawTxn()
    //RawTxnByteArray = new TextEncoder("utf-8").encode(RawTxnString);
    //RawTxnByteArray2 = toUTF8Array(RawTxnString);
    //console.log(RawTxnByteArray)
    //console.log(RawTxnByteArray2)
    //console.log(JSON.stringify(RawTxnByteArray)===JSON.stringify(RawTxnByteArray2)) //false typed array vs array
    //RawTxnHex = toHexString(RawTxnByteArray);
    //var decoded = new TextDecoder("utf-8").decode(txByteArray);
    //$('#rawtxnhex').val(RawTxnHex);
     if( Signature && Signature != ""){
      checkSignature()
    }
  });

  $('#id_sender').on('blur', function() { 
    Sender =  $("#id_sender").val();
    Signature =  $("#id_signature").val();
    if( Sender && Sender != ""){
      checkSender()
    }
    if( Signature && Signature != ""){
      checkSignature()
    }
  });

  $('#id_sender_seq_no').on('blur', function() {
    SeqNo =  $("#id_sender_seq_no").val();
    Signature =  $("#id_signature").val();
    if( SeqNo && SeqNo != ""){
      checkSeqNo()
    }
    if( Signature && Signature != ""){
      checkSignature()
    }       
  });
  $('#id_recipient').on('blur', function() {
    Recipient =  $("#id_recipient").val();
    Signature =  $("#id_signature").val();
    if( Recipient && Recipient != ""){
      checkRecipient()
    }
    if( Signature && Signature != ""){
      checkSignature()
    }   

  });
  $('#id_amount').on('blur', function() { 
    Amount =  $("#id_amount").val();
    Signature =  $("#id_signature").val();
    if( Amount && Amount != ""){
      checkAmount()
    }
    if( Signature && Signature != ""){
      checkSignature()
    }  
  });

  $('#idSignTxn').on('click', function() {
    if(checkFields()){
      $('#signatureModal').modal('show');
    }
  });

  $('#id_signature').on('blur change paste keyup input', function() {
    Signature =  $("#id_signature").val();
    if( Signature && Signature != ""){
      checkSignature()
    }
  });


  $('#CloseModal').on('click', function() {
    $('#modalsecretkey').val('');
    $('#signatureModal').modal('hide');
  });

  $('#GenerateSig').on('click', function() {
    RawTxnByteArray = new TextEncoder("utf-8").encode($('#modalrawtxn').val());
    try{
      //console.log('secretKey')
      //console.log($('#modalsecretkey').val())
      //console.log('secretKeybytes')
      //console.log(fromHexString($('#modalsecretkey').val()) )
      //console.log('keypair.secretKey')
      //console.log(toHexString(( nacl.sign.keyPair.fromSeed(fromHexString($('#modalsecretkey').val())) ).secretKey ))
      Signature = nacl.sign.detached( RawTxnByteArray, ( nacl.sign.keyPair.fromSeed(fromHexString($('#modalsecretkey').val())) ).secretKey );
      $("#modalsecretkey").removeClass("is-invalid");
    } catch(e) {
      //console.log('bad secret key')
      //console.log(e.message)
      //$('#modalsecretkey').val('');
      $("#modalsecretkey").addClass("is-invalid");
      //throw new Exception();
      //throw new Error(e.message);
      //throw "exit";
      return false;
    }
    $('#id_signature').val(toHexString(Signature));
    $('#modalsecretkey').val('');
    $('#signatureModal').modal('hide');
    checkSignature()
    //console.log( new TextDecoder("utf-8").decode(Signature)) ;
    //console.log( new TextDecoder("utf-8").decode(nacl.sign.open(Signature, keypair.publicKey)));
  });

  function validateForm() {
    return checkFields() && checkSignature()
  }



  




 // ATTEMPT AT MAKING TRANSFER DRY

  const fromHexString = hexString =>
    new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
  const toHexString = bytes =>
    bytes.reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');
  function validHex(string) {
    return (toHexString(fromHexString(string)) === string.toLowerCase()) ;
  }
  function validPublicKey(string) {
    return (validHex(string) && string.length == 64) ;
  }
  function checkSignature() {
    var Sender = $("#id_sender_pk").val();
    var TxnString = 'Type:Transfer,Sender:'+ $("#id_sender_pk").val() +',SeqNo:'+ String($("#id_sender_seq_no").val()) +',Recipient:'+ $("#id_recipient_pk").val() +',Amount:'+ String($("#id_amount").val());
    if(TxnString != $("#txnstring").val()){alert('txnstring mismatch!!')};  
    var TxnByteArray = new TextEncoder("utf-8").encode(TxnString);
    var Signature = document.getElementById("id_signature").value;
    try {
      if(nacl.sign.detached.verify(TxnByteArray, fromHexString(Signature), fromHexString(Sender))){
        $("#id_signature").removeClass("is-invalid");
        $("#id_signature").addClass("is-valid");
        return true;
      } else {
        $("#id_signature").removeClass("is-valid");
        $("#id_signature").addClass("is-invalid");
        return false;
      }
    } catch(e) {
      $("#id_signature").removeClass("is-valid");
      $("#id_signature").addClass("is-invalid");
      return false;
    }
  }

  $("#id_sender_pk,#id_sender_seq_no,#id_recipient_pk,#id_amount,#id_signature").on("change paste keyup input", function() {
    var TxnString = 'Type:Transfer,Sender:'+ $("#id_sender_pk").val() +',SeqNo:'+ String($("#id_sender_seq_no").val()) +',Recipient:'+ $("#id_recipient_pk").val() +',Amount:'+ String($("#id_amount").val());
    $('#txnstring').val(TxnString);
    $('#modal_txnstring').val(TxnString);
    if($("#id_signature").val() != ""){
      checkSignature()
    }
  });

  $('#id_sender_pk,#id_recipient_pk').on('blur', function() { 
    if($(this).val() != ""){
      if(!validPublicKey($(this).val())){
        $('#'+$(this).attr("id")+'_feedback').text('Not a valid public key.');
        $(this).addClass("is-invalid");
      } else {
        $(this).removeClass("is-invalid");
      };
    };
  });

  $('#id_sender_seq_no,#id_amount').on('blur', function() { 
    if($(this).val() != ""){
      $(this).removeClass("is-invalid");
    };
  });

  $('#id_signature').on('blur', function() { 
    if($("#id_signature").val() != ""){
      checkSignature()
    } else {
      $("#id_signature").removeClass("is-invalid");
    }
  });

  function checkFields() {
    var is_valid = true;
    var fields = ["#id_sender_pk","#id_sender_seq_no","#id_recipient_pk","#id_amount"];
    for (var i = 0; i < 4; i++) {
      if($(fields[i]).val()==''){
        $(fields[i]+"_feedback").text('This field is required.');
        $(fields[i]).addClass("is-invalid");
        is_valid = false;
      } else {
        $(fields[i]).removeClass("is-invalid");
      }
    }
    return is_valid;
  }

  $('#idSignTxn').on('click', function() {
    if(checkFields()){
      $('#signatureModal').modal('show');
    }
  });

  $('#CloseModal').on('click', function() {
    $('#modalsecretkey').val('');
    $('#signatureModal').modal('hide');
  });

  $('#GenerateSig').on('click', function() {
    var TxnByteArray = new TextEncoder("utf-8").encode($('#modal_txnstring').val());
    var Signature;
    try{
      Signature = nacl.sign.detached( TxnByteArray, ( nacl.sign.keyPair.fromSeed(fromHexString($('#modalsecretkey').val())) ).secretKey );
      $("#modalsecretkey").removeClass("is-invalid");
    } catch(e) {
      $("#modalsecretkey").addClass("is-invalid");
      return false;
    }
    $('#id_signature').val(toHexString(Signature));
    $('#modalsecretkey').val('');
    $('#signatureModal').modal('hide');
    checkSignature()
  });

  function validateForm() {
    return checkFields() && checkSignature()
  }
