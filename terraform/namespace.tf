resource "kubernetes_namespace" "chat-app-ns" {
  metadata {
    name = "chat-app"
  }
}