const { onRequest } = require("firebase-functions/v2/https");
const admin = require("firebase-admin");
admin.initializeApp();

const db = admin.database();

// ===============================================
//  DO NOT MODIFY — Your ORIGINAL upload function
// ===============================================
exports.iotUpload = onRequest(async (req, res) => {
  try {
    if (req.method !== "POST") {
      return res.status(405).send("Only POST allowed");
    }

    const data = req.body;

    const deviceId = data.deviceId;
    const timestamp = data.timestamp;
    const payload = data.payload;

    if (!deviceId || !payload) {
      return res.status(400).send("Missing required fields");
    }

    // Save log
    const logRef = db.ref(`smartbus/${deviceId}/logs`).push();
    await logRef.set({
      timestamp,
      ...payload,
    });

    // Update latest snapshot
    await db.ref(`smartbus/${deviceId}/latest`).set({
      timestamp,
      ...payload,
    });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error("Upload error:", err);
    return res.status(500).send("Server error");
  }
});

