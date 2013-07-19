<?php
// Set the URL and port of the destination server
$url = "ec2-55-555-555-555.compute-1.amazonaws.com:8080";
 
// Set up request and headers
$req = 'ok_verify=true'; 
foreach ($_POST as $key => $value) { 
	$value = urlencode(stripslashes($value)); 
	$req .= "&$key=$value"; 
} 
$header = "POST /ipn-verify.html HTTP/1.0\r\n"; 
$header .= "Host: www.okpay.com\r\n"; 
$header .= "Content-Type: application/x-www-form-urlencoded\r\n"; 
$header .= "Content-Length: " . strlen($req) . "\r\n\r\n"; 
$fp = fsockopen ('www.okpay.com', 80, $errno, $errstr, 30); 

// Forward or exit, depending on the IPN verification response
if (!$fp) { 
	# Error 
} else { 
	fputs ($fp, $header . $req); 
	while (!feof($fp)) { 
		$res = fgets ($fp, 1024); 
		if (strcmp ($res, "VERIFIED") == 0) { 
			echo 'IPN VERIFIED'; 
            $ch = curl_init();
			curl_setopt($ch,CURLOPT_URL, $url);
			curl_setopt($ch,CURLOPT_POST, 1);
			curl_setopt($ch,CURLOPT_POSTFIELDS, $req);
			$result = curl_exec($ch);
			curl_close($ch);

		} elseif (strcmp ($res, "TEST")== 0) { 
			echo 'TEST IPN'; 
            $ch = curl_init();
			curl_setopt($ch,CURLOPT_URL, $url);
			curl_setopt($ch,CURLOPT_POST, 1);
			curl_setopt($ch,CURLOPT_POSTFIELDS, $req);
			$result = curl_exec($ch);
			curl_close($ch);

		} elseif (strcmp ($res, "INVALID") == 0) { 
			echo 'IPN INVALID'; 		
		} 
	} 
	fclose ($fp); 
} 
?> 		