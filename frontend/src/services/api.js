/**
 * API 客户端 - 自动选择移动端或 Web 端实现
 */
import { Capacitor } from '@capacitor/core';
import { MobileAPI } from '@/mobile-services/mobile-api';
// 动态导入 Web API（避免在移动端打包无用代码）
let webAPI = null;
/**
 * 获取 API 实例
 */
async function getAPI() {
    const platform = Capacitor.getPlatform();
    const isNative = platform === 'ios' || platform === 'android';
    if (isNative) {
        // 移动端：使用本地 API
        const mobileAPI = new MobileAPI();
        await mobileAPI.initialize();
        return mobileAPI;
    }
    else {
        // Web 端：使用 HTTP API
        if (!webAPI) {
            const module = await import('./web-api');
            webAPI = module.api;
        }
        return webAPI;
    }
}
// 创建 API 代理，延迟初始化
export const api = new Proxy({}, {
    get: (_target, prop) => {
        return async (...args) => {
            const apiInstance = await getAPI();
            const method = apiInstance[prop];
            if (typeof method !== 'function') {
                throw new Error(`API method ${prop} not found`);
            }
            return method.apply(apiInstance, args);
        };
    }
});
/**
 * 检查是否为移动端环境
 */
export function isMobilePlatform() {
    const platform = Capacitor.getPlatform();
    return platform === 'ios' || platform === 'android';
}
/**
 * 获取当前平台信息
 */
export function getPlatformInfo() {
    return {
        platform: Capacitor.getPlatform(),
        isNative: Capacitor.isNativePlatform(),
        version: '1.0.0'
    };
}
