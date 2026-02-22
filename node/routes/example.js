const express = require("express");

const router = express.Router();

router.get("/hello", (_req, res) => {
  res.json({
    ok: true,
    message: "Hola desde el servidor local Node.js",
    timestamp: new Date().toISOString()
  });
});

module.exports = router;

