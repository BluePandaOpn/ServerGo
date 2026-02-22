const fs = require("fs");
const http = require("http");
const https = require("https");
const path = require("path");
const express = require("express");
const cors = require("cors");
const selfsigned = require("selfsigned");

const exampleRoutes = require("./routes/example");

const app = express();
const rootDir = path.resolve(__dirname, "..");
const configPath = path.join(rootDir, "config.json");
const rawConfig = fs.existsSync(configPath)
  ? JSON.parse(fs.readFileSync(configPath, "utf8"))
  : {};

const config = {
  defaultPort: 3000,
  https: {
    enabled: false,
    autoGenerateCert: true,
    keyPath: "certs/server.key",
    certPath: "certs/server.crt",
    redirectHttp: true,
    httpPort: 8080
  },
  ...rawConfig,
  https: {
    enabled: false,
    autoGenerateCert: true,
    keyPath: "certs/server.key",
    certPath: "certs/server.crt",
    redirectHttp: true,
    httpPort: 8080,
    ...(rawConfig.https || {})
  }
};

const port = Number(process.env.PORT || config.defaultPort || 3000);
const httpsEnabled = Boolean(config.https.enabled);

app.use(cors());
app.use(express.json());

app.use("/api", exampleRoutes);
app.use(express.static(path.join(__dirname, "public")));

app.get("/api/health", (_req, res) => {
  res.json({ ok: true, service: "servergo-platform", https: httpsEnabled, port });
});

if (httpsEnabled) {
  const tlsOptions = ensureLocalTls(config.https, rootDir);
  https.createServer(tlsOptions, app).listen(port, () => {
    console.log(`[NODE] Servidor HTTPS en https://localhost:${port}`);
  });
  if (config.https.redirectHttp) {
    const httpPort = Number(config.https.httpPort || 8080);
    http
      .createServer((req, res) => {
        const host = (req.headers.host || "localhost").split(":")[0];
        const targetPort = port === 443 ? "" : `:${port}`;
        const target = `https://${host}${targetPort}${req.url}`;
        res.statusCode = 301;
        res.setHeader("Location", target);
        res.end();
      })
      .listen(httpPort, () => {
        console.log(`[NODE] Redirect HTTP->HTTPS en http://localhost:${httpPort}`);
      });
  }
} else {
  app.listen(port, () => {
    console.log(`[NODE] Servidor HTTP en http://localhost:${port}`);
  });
}

function ensureLocalTls(httpsCfg, rootDirPath) {
  const keyAbs = path.resolve(rootDirPath, httpsCfg.keyPath || "certs/server.key");
  const certAbs = path.resolve(rootDirPath, httpsCfg.certPath || "certs/server.crt");
  const keyExists = fs.existsSync(keyAbs);
  const certExists = fs.existsSync(certAbs);
  if (!keyExists || !certExists) {
    if (!httpsCfg.autoGenerateCert) {
      throw new Error(`Certificados HTTPS no encontrados: ${keyAbs} / ${certAbs}`);
    }
    fs.mkdirSync(path.dirname(keyAbs), { recursive: true });
    fs.mkdirSync(path.dirname(certAbs), { recursive: true });
    const attrs = [{ name: "commonName", value: "localhost" }];
    const pems = selfsigned.generate(attrs, {
      days: 3650,
      keySize: 2048,
      algorithm: "sha256"
    });
    fs.writeFileSync(keyAbs, pems.private, "utf8");
    fs.writeFileSync(certAbs, pems.cert, "utf8");
    console.log(`[NODE] Certificado local generado en ${keyAbs} y ${certAbs}`);
  }
  return {
    key: fs.readFileSync(keyAbs, "utf8"),
    cert: fs.readFileSync(certAbs, "utf8")
  };
}
