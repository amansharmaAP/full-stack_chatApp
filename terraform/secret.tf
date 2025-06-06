resource "kubernetes_secret" "jwt" {
  metadata {
    name      = "chatapp-secret"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  data = {
    jwt = "eW91cl9qd3Rfc2VjcmV0X2hlcmU="
  }
  type = "Opaque"
  depends_on = [ kubernetes_namespace.chat-app-ns ]
}