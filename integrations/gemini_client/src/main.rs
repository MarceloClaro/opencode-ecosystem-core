// gemini-client — executor Gemini portátil (SPEC-935-R1001).
//
// Lê o prompt de stdin, chama a API Gemini (generateContent) com GEMINI_API_KEY
// e imprime o texto da resposta. Não usa OAuth, keyring nem o CLI `agy`.
//
// TLS: aceita qualquer certificado (NoVerify) porque, dentro do sandbox
// OpenShell, o proxy de rede faz MITM TLS com certificado próprio; a conexão
// termina em Google com TLS correto do lado do proxy. Fora do sandbox, prefira
// um cliente com verificação TLS normal.
//
// Uso:
//   printf 'pergunta' | GEMINI_API_KEY=... [GEMINI_MODEL=gemini-3.5-flash] ./gemini-client
use std::io::Read;
use std::env;
use std::sync::Arc;

#[derive(Debug)]
struct NoVerify;
impl rustls::client::danger::ServerCertVerifier for NoVerify {
    fn verify_server_cert(&self, _e: &rustls::pki_types::CertificateDer, _i: &[rustls::pki_types::CertificateDer], _s: &rustls::pki_types::ServerName, _o: &[u8], _n: rustls::pki_types::UnixTime) -> Result<rustls::client::danger::ServerCertVerified, rustls::Error> {
        Ok(rustls::client::danger::ServerCertVerified::assertion())
    }
    fn verify_tls12_signature(&self, _m: &[u8], _c: &rustls::pki_types::CertificateDer, _d: &rustls::DigitallySignedStruct) -> Result<rustls::client::danger::HandshakeSignatureValid, rustls::Error> {
        Ok(rustls::client::danger::HandshakeSignatureValid::assertion())
    }
    fn verify_tls13_signature(&self, _m: &[u8], _c: &rustls::pki_types::CertificateDer, _d: &rustls::DigitallySignedStruct) -> Result<rustls::client::danger::HandshakeSignatureValid, rustls::Error> {
        Ok(rustls::client::danger::HandshakeSignatureValid::assertion())
    }
    fn supported_verify_schemes(&self) -> Vec<rustls::SignatureScheme> {
        vec![rustls::SignatureScheme::RSA_PKCS1_SHA256, rustls::SignatureScheme::ECDSA_NISTP256_SHA256, rustls::SignatureScheme::ED25519]
    }
}

fn main() {
    let _ = rustls::crypto::ring::default_provider().install_default();
    let key = env::var("GEMINI_API_KEY").expect("GEMINI_API_KEY");
    let model = env::var("GEMINI_MODEL").unwrap_or_else(|_| "gemini-3.5-flash".to_string());
    let mut prompt = String::new();
    std::io::stdin().read_to_string(&mut prompt).expect("stdin");
    let cfg = rustls::ClientConfig::builder().dangerous().with_custom_certificate_verifier(Arc::new(NoVerify)).with_no_client_auth();
    let agent = ureq::AgentBuilder::new().tls_config(Arc::new(cfg)).build();
    let url = format!("https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}", model, key);
    let body = serde_json::json!({"contents":[{"parts":[{"text": prompt}]}]}).to_string();
    let resp = agent.post(&url).set("Content-Type", "application/json").send_string(&body);
    let text = match resp {
        Ok(r) => r.into_string().unwrap_or_default(),
        Err(e) => {
            // A URL do erro contém ?key=<GEMINI_API_KEY>; redigir para não vazar a chave.
            let message = format!("{}", e).replace(&key, "REDACTED");
            eprintln!("GEMINI_ERROR:{}", message);
            std::process::exit(1);
        }
    };
    let v: serde_json::Value = match serde_json::from_str(&text) { Ok(v) => v, Err(_) => { eprintln!("GEMINI_NONJSON:{}", &text[..text.len().min(200)]); std::process::exit(2); } };
    if let Some(t) = v["candidates"][0]["content"]["parts"][0]["text"].as_str() { print!("{}", t); }
    else if let Some(m) = v["error"]["message"].as_str() { eprintln!("GEMINI_API_ERROR:{}", m); std::process::exit(3); }
    else { eprintln!("GEMINI_UNEXPECTED"); std::process::exit(4); }
}
