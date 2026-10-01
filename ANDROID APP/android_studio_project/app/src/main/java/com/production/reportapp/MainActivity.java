package com.production.reportapp;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "ReportAppPrefs";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String DEFAULT_HOST = "DESKTOP-ITTFPI2.local";
    private static final String DEFAULT_PORT = "5050";
    private static final int FILE_CHOOSER_REQUEST_CODE = 1001;

    private WebView webView;
    private ProgressBar progressBar;
    private View errorLayout;
    private TextView errorTextView;
    private SharedPreferences prefs;
    private ValueCallback<Uri[]> uploadMessage;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        errorLayout = findViewById(R.id.errorLayout);
        errorTextView = findViewById(R.id.errorTextView);

        Button btnSettings = findViewById(R.id.btnChangeServer);
        if (btnSettings != null) {
            btnSettings.setOnClickListener(v -> showServerConfigDialog());
        }

        Button btnRetry = findViewById(R.id.btnRetry);
        if (btnRetry != null) {
            btnRetry.setOnClickListener(v -> loadCurrentServer());
        }

        configureWebView();

        String currentUrl = getServerUrl();
        if (currentUrl == null || currentUrl.isEmpty()) {
            showServerConfigDialog();
        } else {
            loadCurrentServer();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            CookieManager.getInstance().flush();
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(true);

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true);
        }

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
                errorLayout.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    CookieManager.getInstance().flush();
                }
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    progressBar.setVisibility(View.GONE);
                    webView.setVisibility(View.GONE);
                    errorLayout.setVisibility(View.VISIBLE);
                    String url = getServerUrl();
                    errorTextView.setText("Cannot connect to server at:\n" + url + "\n\nTip: Did your Wi-Fi network or IP change?");
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress < 100) {
                    progressBar.setVisibility(View.VISIBLE);
                    progressBar.setProgress(newProgress);
                } else {
                    progressBar.setVisibility(View.GONE);
                }
            }

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
                if (uploadMessage != null) {
                    uploadMessage.onReceiveValue(null);
                }
                uploadMessage = filePathCallback;

                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
                startActivityForResult(Intent.createChooser(intent, "Select Job / CAD File"), FILE_CHOOSER_REQUEST_CODE);
                return true;
            }
        });

        webView.setDownloadListener((url, userAgent, contentDisposition, mimetype, contentLength) -> {
            try {
                String filename = URLUtil.guessFileName(url, contentDisposition, mimetype);
                DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                request.setMimeType(mimetype);

                String cookies = CookieManager.getInstance().getCookie(url);
                request.addRequestHeader("cookie", cookies);
                request.addRequestHeader("User-Agent", userAgent);
                request.setDescription("Downloading report from Production System...");
                request.setTitle(filename);
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename);

                DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                if (dm != null) {
                    dm.enqueue(request);
                    Toast.makeText(MainActivity.this, "Downloading " + filename + " to Downloads folder...", Toast.LENGTH_SHORT).show();
                }
            } catch (Exception e) {
                Toast.makeText(MainActivity.this, "Download failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private String getServerUrl() {
        return prefs.getString(KEY_SERVER_URL, "http://" + DEFAULT_HOST + ":" + DEFAULT_PORT + "/portal");
    }

    private void saveServerUrl(String url) {
        prefs.edit().putString(KEY_SERVER_URL, url).apply();
    }

    private void loadCurrentServer() {
        String url = getServerUrl();
        progressBar.setVisibility(View.VISIBLE);
        errorLayout.setVisibility(View.GONE);
        webView.setVisibility(View.VISIBLE);
        webView.loadUrl(url);
    }

    public void showServerConfigDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_server_config, null);
        builder.setView(dialogView);

        EditText etHost = dialogView.findViewById(R.id.etHost);
        EditText etPort = dialogView.findViewById(R.id.etPort);
        Button btnMdns = dialogView.findViewById(R.id.btnUseMdns);
        Button btnAutoScan = dialogView.findViewById(R.id.btnAutoScan);

        String curUrl = getServerUrl();
        try {
            Uri uri = Uri.parse(curUrl);
            if (uri.getHost() != null) etHost.setText(uri.getHost());
            if (uri.getPort() != -1) etPort.setText(String.valueOf(uri.getPort()));
            else etPort.setText(DEFAULT_PORT);
        } catch (Exception e) {
            etHost.setText(DEFAULT_HOST);
            etPort.setText(DEFAULT_PORT);
        }

        AlertDialog dialog = builder.create();

        btnMdns.setOnClickListener(v -> {
            etHost.setText(DEFAULT_HOST);
            etPort.setText(DEFAULT_PORT);
        });

        btnAutoScan.setOnClickListener(v -> {
            btnAutoScan.setEnabled(false);
            btnAutoScan.setText("Scanning Wi-Fi...");
            new SubnetScannerTask(etHost, btnAutoScan).execute();
        });

        dialogView.findViewById(R.id.btnSaveConnect).setOnClickListener(v -> {
            String host = etHost.getText().toString().trim();
            String port = etPort.getText().toString().trim();

            if (host.isEmpty()) {
                etHost.setError("Please enter Hostname or IP address");
                return;
            }
            if (port.isEmpty()) port = DEFAULT_PORT;

            String newUrl = "http://" + host + ":" + port + "/portal";
            saveServerUrl(newUrl);
            dialog.dismiss();
            loadCurrentServer();
        });

        dialog.show();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (uploadMessage == null) return;
            uploadMessage.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            uploadMessage = null;
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_server_settings) {
            showServerConfigDialog();
            return true;
        } else if (item.getItemId() == R.id.action_reload) {
            loadCurrentServer();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    private static class SubnetScannerTask extends AsyncTask<Void, Void, String> {
        private final EditText etHost;
        private final Button btnScan;

        SubnetScannerTask(EditText etHost, Button btnScan) {
            this.etHost = etHost;
            this.btnScan = btnScan;
        }

        @Override
        protected String doInBackground(Void... voids) {
            if (isPortOpen(DEFAULT_HOST, 5050, 600)) {
                return DEFAULT_HOST;
            }
            String[] subnets = {"192.168.1.", "192.168.0.", "192.168.43."};
            for (String sub : subnets) {
                for (int i = 2; i <= 254; i++) {
                    String candidate = sub + i;
                    if (isPortOpen(candidate, 5050, 40)) {
                        return candidate;
                    }
                }
            }
            return null;
        }

        private boolean isPortOpen(String host, int port, int timeoutMs) {
            try (Socket socket = new Socket()) {
                socket.connect(new InetSocketAddress(host, port), timeoutMs);
                return true;
            } catch (IOException e) {
                return false;
            }
        }

        @Override
        protected void onPostExecute(String foundHost) {
            btnScan.setEnabled(true);
            btnScan.setText("Auto-Scan Wi-Fi");
            if (foundHost != null) {
                etHost.setText(foundHost);
                Toast.makeText(etHost.getContext(), "Found Server at: " + foundHost, Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(etHost.getContext(), "Could not auto-detect. Please enter IP manually.", Toast.LENGTH_LONG).show();
            }
        }
    }
}
