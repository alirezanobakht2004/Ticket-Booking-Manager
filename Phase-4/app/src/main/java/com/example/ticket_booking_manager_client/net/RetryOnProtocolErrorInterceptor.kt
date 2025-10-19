package com.example.ticket_booking_manager_client.net

import android.util.Log
import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException
import java.net.ProtocolException

class RetryOnProtocolErrorInterceptor(
    private val tag: String = "APP/HTTP_RETRY"
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val req = chain.request()
        val isGet = req.method.equals("GET", ignoreCase = true)
        return try {
            chain.proceed(req)
        } catch (e: ProtocolException) {
            if (isGet) {
                Log.w(tag, "ProtocolException on GET. Retrying once: ${req.url} (${e.message})")
                chain.proceed(req)
            } else {
                throw e
            }
        } catch (e: IOException) {
            throw e
        }
    }
}