// The authenticate function is called whenever ZAP requires to authenticate, for a Context for which this script
// was selected as the Authentication Method. The function should send any messages that are required to do the authentication
// and should return a message with an authenticated response so the calling method.
//
// NOTE: Any message sent in the function should be obtained using the 'helper.prepareMessage()' method.
//
// Parameters:
//		helper - a helper class providing useful methods: prepareMessage(), sendAndReceive(msg)
//		paramsValues - the values of the parameters configured in the Session Properties -> Authentication panel.
//					The paramsValues is a map, having as keys the parameters names (as returned by the getRequiredParamsNames()
//					and getOptionalParamsNames() functions below)
//		credentials - an object containing the credentials values, as configured in the Session Properties -> Users panel.
//					The credential values can be obtained via calls to the getParam(paramName) method. The param names are the ones
//					returned by the getCredentialsParamsNames() below

function authenticate(helper, paramsValues, credentials) {
    var loginUrl = paramsValues.get("Login_URL");
    var postHeader = paramsValues.get("POST_Header");
    var clientSecret = "someClientSecret";
    var grantType = "something";
    var scopeId= "openid";
    var postData = "grant_type={%grantType%}&client_secret={%password%}&scope={%scopeId%}";
    var csrfTokenName = paramsValues.get("CSRF_Field");
    var ScriptVars    = Java.type('org.zaproxy.zap.extension.script.ScriptVars');
  
    postData = postData.replace('{%password%}', encodeURIComponent(clientSecret));
    postData = postData.replace('{%grantType%}', encodeURIComponent(grantType));
    postData = postData.replace('{%scopeId%}', encodeURIComponent(scopeId));
    
    print("---- Authentication script has started ----");
    var msg = sendAndReceive(helper, loginUrl, postHeader, postData);
    var postResponse = msg.getResponseBody().toString()
    var token = getTokenValue(postResponse, csrfTokenName);
    ScriptVars.setGlobalVar("acess-token",token)
    return msg;
  }
  
  function getRequiredParamsNames() {
    return [ "Login_URL", "CSRF_Field", "POST_Data" , "POST_Header"];
  }
  
  function getTokenValue(tokenResponse, tokenName) {
    var jsonValues = tokenResponse.split('"');
    var tokenValue = jsonValues[3];
    return tokenValue 
  }
  
  function sendAndReceive(helper, url, postHeader, postData) {
    var HttpRequestHeader = Java.type('org.parosproxy.paros.network.HttpRequestHeader');
    var HttpHeader = Java.type('org.parosproxy.paros.network.HttpHeader');
    var URI = Java.type('org.apache.commons.httpclient.URI');
    var requestMethod = HttpRequestHeader.POST;
    var requestUri = new URI(url, false);
    var msg = helper.prepareMessage();
    
    // Build the submission request header
    var requestHeader = new HttpRequestHeader(requestMethod, requestUri, HttpHeader.HTTP11);
    msg.setRequestHeader(requestHeader);
    msg.setRequestBody(postData);
    msg.getRequestHeader().setContentLength(msg.getRequestBody().length());
  
    helper.sendAndReceive(msg,true);
    return msg
  }
  
  function getOptionalParamsNames() {
    return [];
  }
  
  function getCredentialsParamsNames() {
    return [ "Username", "Password" ];
  }