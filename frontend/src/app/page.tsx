"use client";

import { useState } from "react";
import { Alert, Badge, Button, Card, Col, Container, Row } from "react-bootstrap";
import { useFiles } from "../hooks/useFiles";
import { useAlerts } from "../hooks/useAlerts";
import { FileList } from "../components/FileList";
import { AlertList } from "../components/AlertList";
import { UploadModal } from "../components/UploadModal";

export default function Page() {
  const { files, isLoading: filesLoading, error: filesError, loadFiles, upload } = useFiles();
  const { alerts, isLoading: alertsLoading, error: alertsError } = useAlerts();
  const [showModal, setShowModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleUpload = async (title: string, file: File) => {
    try {
      await upload(title, file);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Ошибка загрузки");
      throw err;
    }
  };

  const combinedError = filesError || alertsError || errorMessage;

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <Card className="shadow-sm border-0 mb-4">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                <div>
                  <h1 className="h3 mb-2">Управление файлами</h1>
                  <p className="text-secondary mb-0">
                    Загрузка файлов, просмотр статусов обработки и ленты алертов.
                  </p>
                </div>
                <div className="d-flex gap-2">
                  <Button variant="outline-secondary" onClick={loadFiles}>
                    Обновить
                  </Button>
                  <Button variant="primary" onClick={() => setShowModal(true)}>
                    Добавить файл
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {combinedError && (
            <Alert variant="danger" className="shadow-sm">
              {combinedError}
            </Alert>
          )}

          <Card className="shadow-sm border-0 mb-4">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Файлы</h2>
                <Badge bg="secondary">{files.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <FileList files={files} isLoading={filesLoading} onRefresh={loadFiles} />
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Алерты</h2>
                <Badge bg="secondary">{alerts.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <AlertList alerts={alerts} isLoading={alertsLoading} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <UploadModal
        show={showModal}
        onHide={() => setShowModal(false)}
        onUpload={handleUpload}
      />
    </Container>
  );
}