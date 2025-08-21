package com.example.ticket_booking_manager_client.net

import android.util.Log
import okhttp3.Interceptor
import okhttp3.Response
import okio.Buffer
import okio.GzipSource
import java.io.IOException
import java.nio.charset.Charset
import java.util.concurrent.atomic.AtomicLong

class SafeBodyLoggingInterceptor(
    private val tag: String = "APP/HTTP_BODY",
    private val maxBodyChars: Int = 20000
) : Interceptor {

    companion object {
        private val COUNTER = AtomicLong(1)
        private val UTF8 = Charset.forName("UTF-8")
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        val id = COUNTER.getAndIncrement()
        val request = chain.request()
        val noPeek = request.header("X-No-Peek") == "1"

        Log.d(tag, "--> [#${id}] ${request.method} ${request.url}")

        request.headers.forEach {
            Log.d(tag, "[#${id}] ReqHdr: ${it.first}: ${it.second}")
        }

        request.body?.let { body ->
            try {
                val buffer = Buffer()
                body.writeTo(buffer)
                var charset = UTF8
                val contentType = body.contentType()
                if (contentType != null) {
                    charset = contentType.charset(UTF8) ?: UTF8
                }
                val content = buffer.readString(charset)
                Log.d(tag, "[#${id}] ReqBody (${content.length} chars): " + content.take(maxBodyChars))
            } catch (e: Exception) {
                Log.e(tag, "[#${id}] ReqBody error: ${e.message}", e)
            }
        }

        val startNs = System.nanoTime()
        return try {
            val response = chain.proceed(request)
            val tookMs = (System.nanoTime() - startNs) / 1e6
            Log.d(tag, "<-- [#${id}] ${response.code} ${response.message} (${tookMs}ms) ${response.request.url}")

            response.headers.forEach {
                Log.d(tag, "[#${id}] ResHdr: ${it.first}: ${it.second}")
            }

            val responseBody = response.body
            if (responseBody == null) {
                Log.d(tag, "[#${id}] ResBody: <null>")
                return response
            }

            if (noPeek) {
                Log.d(tag, "[#${id}] ResBody: <skipped by X-No-Peek>")
                return response
            }

            val source = responseBody.source()
            source.request(Long.MAX_VALUE)
            var buffer = source.buffer.clone()

            val contentEncoding = response.headers["Content-Encoding"]
            if (contentEncoding != null && contentEncoding.equals("gzip", ignoreCase = true)) {
                try {
                    GzipSource(buffer.clone()).use { gz ->
                        val unzipped = Buffer()
                        unzipped.writeAll(gz)
                        buffer = unzipped
                    }
                } catch (e: Exception) {
                    Log.e(tag, "[#${id}] Gzip decode failed: ${e.message}", e)
                }
            }

            var charset = UTF8
            val contentType = responseBody.contentType()
            if (contentType != null) {
                charset = contentType.charset(UTF8) ?: UTF8
            }

            val content = try {
                buffer.readString(charset)
            } catch (e: Exception) {
                "[[Body read error: ${e.message}]]"
            }

            Log.d(tag, "[#${id}] ResBody (${content.length} chars): " + content.take(maxBodyChars))
            response
        } catch (e: IOException) {
            val tookMs = (System.nanoTime() - startNs) / 1e6
            Log.e(tag, "<-- [#${id}] FAILURE after ${tookMs}ms: ${e.javaClass.simpleName}: ${e.message}", e)
            throw e
        }
    }
}